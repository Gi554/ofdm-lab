"""Transport RGB8 brut par paquets fixes, CRC32 distincts en-tête et données."""

import struct
import zlib
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import matplotlib.image as mpimg
import numpy as np

from .noise import _positive_integer

# magic/version/canaux, largeur/hauteur, octets totaux, séquence/nombre, utilisés,
# CRC du bloc et CRC global de l’image.
_FIELDS = struct.Struct(">4sBBHHIIIHII")
HEADER_BYTES = _FIELDS.size + 4
MAX_IMAGE_BYTES = 4 * 1024 * 1024


def _chunk_size(value):
    size = _positive_integer(value, "Les octets par paquet")
    if size % 3 or size > 65535:
        raise ValueError("Le bloc RGB doit être multiple de 3 et <=65535 octets.")
    return size


def validate_image(image):
    values = np.asarray(image)
    if values.dtype != np.uint8 or values.ndim != 3 or values.shape[2] != 3:
        raise ValueError("Une image RGB uint8 de forme H×W×3 est requise.")
    if not values.size or values.size > MAX_IMAGE_BYTES or max(values.shape[:2]) > 65535:
        raise ValueError("Dimensions vides ou trop grandes pour le format RGB8 du laboratoire.")
    return np.ascontiguousarray(values)


def load_image(path):
    """Charger un PNG local RGB, gris ou RGBA ; alpha composé sur fond blanc."""
    if isinstance(path, bytes):
        values = np.asarray(mpimg.imread(BytesIO(path), format="png"))
    else:
        if Path(path).suffix.lower() != ".png":
            raise ValueError("Le chargeur du laboratoire accepte un fichier PNG local.")
        values = np.asarray(mpimg.imread(path))
    if values.dtype.kind == "f":
        if not np.all(np.isfinite(values)) or np.any((values < 0) | (values > 1)):
            raise ValueError("Les composantes PNG doivent être finies entre 0 et 1.")
        values = np.rint(values * 255).astype(np.uint8)
    if values.dtype != np.uint8:
        raise ValueError("Le PNG doit pouvoir être représenté en composantes 8 bits.")
    if values.ndim == 2:
        values = np.repeat(values[..., None], 3, axis=2)
    if values.ndim == 3 and values.shape[2] == 4:
        alpha = values[..., 3:4].astype(float) / 255
        values = np.rint(values[..., :3] * alpha + 255 * (1 - alpha)).astype(np.uint8)
    return validate_image(values)


def save_image(path, image):
    """Écrire la représentation RGB8 reçue, sans métadonnée de l'image originale."""
    mpimg.imsave(path, validate_image(image))


def encode_image(image, chunk_bytes=192):
    """En-tête répété par paquet ; zéro-padding du dernier bloc hors CRC utile."""
    values = validate_image(image)
    size = _chunk_size(chunk_bytes)
    height, width, _ = values.shape
    payload = values.tobytes(order="C")
    count = (len(payload) + size - 1) // size
    image_crc = zlib.crc32(payload)
    packets = []
    for index in range(count):
        chunk = payload[index * size : (index + 1) * size]
        header = _FIELDS.pack(
            b"OFLI",
            1,
            3,
            width,
            height,
            len(payload),
            index,
            count,
            len(chunk),
            zlib.crc32(chunk),
            image_crc,
        )
        packets.append(
            header + struct.pack(">I", zlib.crc32(header)) + chunk + bytes(size - len(chunk))
        )
    return b"".join(packets)


@dataclass(frozen=True)
class ImageReception:
    """Deux vues : données à en-tête fiable et données CRC valides ; magenta = effacement."""

    diagnostic: np.ndarray | None
    accepted: np.ndarray | None
    known_bytes: np.ndarray | None
    accepted_bytes: np.ndarray | None
    expected_packets: int | None
    valid_packets: int
    corrupt_payload_packets: int
    invalid_header_packets: int
    missing_packets: int | None
    truncated_bytes: int
    image_crc_valid: bool | None = None


def decode_image(data: bytes, chunk_bytes=192):
    """Reconstruire seulement depuis les en-têtes reçus vérifiés, sans image oracle.

    Taille physique du paquet et frontières supposées connues. Réordonnancement
    accepté ; duplications et métadonnées contradictoires rejetées. Un paquet tronqué
    est un effacement. CRC32 détecte mais ne corrige pas et n'est pas une authentification.
    """
    size = _chunk_size(chunk_bytes)
    width_packet = HEADER_BYTES + size
    if not isinstance(data, bytes):
        raise ValueError("Le transport reçu doit être une suite bytes.")
    metadata = None
    chunks = {}
    invalid = 0
    for start in range(0, len(data) - width_packet + 1, width_packet):
        packet = data[start : start + width_packet]
        header = packet[: _FIELDS.size]
        if zlib.crc32(header) != struct.unpack(">I", packet[_FIELDS.size : HEADER_BYTES])[0]:
            invalid += 1
            continue
        magic, version, channels, width, height, total, index, count, used, crc, image_crc = (
            _FIELDS.unpack(header)
        )
        expected = (total + size - 1) // size
        if (
            magic != b"OFLI"
            or version != 1
            or channels != 3
            or width == 0
            or height == 0
            or total != width * height * 3
            or total > MAX_IMAGE_BYTES
            or count != expected
            or index >= count
            or used != min(size, total - index * size)
        ):
            invalid += 1
            continue
        current = (width, height, total, count, image_crc)
        if metadata is not None and current != metadata:
            raise ValueError(
                "Métadonnées contradictoires : les paquets ne décrivent pas une seule image."
            )
        metadata = current
        if index in chunks:
            raise ValueError("Numéro de paquet dupliqué ; réassemblage ambigu.")
        chunk = packet[HEADER_BYTES : HEADER_BYTES + used]
        chunks[index] = (chunk, zlib.crc32(chunk) == crc)
    trailing = len(data) % width_packet
    if metadata is None:
        return ImageReception(None, None, None, None, None, 0, 0, invalid, None, trailing)
    width, height, total, count, image_crc = metadata
    diagnostic = np.tile(np.array([255, 0, 255], dtype=np.uint8), total // 3)
    accepted = diagnostic.copy()
    known = np.zeros(total, dtype=bool)
    valid = known.copy()
    good = bad = 0
    for index, (chunk, crc_valid) in chunks.items():
        target = slice(index * size, index * size + len(chunk))
        diagnostic[target] = np.frombuffer(chunk, dtype=np.uint8)
        known[target] = True
        if crc_valid:
            accepted[target] = np.frombuffer(chunk, dtype=np.uint8)
            valid[target] = True
            good += 1
        else:
            bad += 1
    image_crc_valid = None
    if good == count:
        image_crc_valid = zlib.crc32(accepted.tobytes()) == image_crc
        if not image_crc_valid:
            raise ValueError("CRC global image invalide malgré les CRC de blocs valides.")
    shape = (height, width, 3)
    return ImageReception(
        diagnostic.reshape(shape),
        accepted.reshape(shape),
        known.reshape(shape),
        valid.reshape(shape),
        count,
        good,
        bad,
        invalid,
        count - len(chunks),
        trailing,
        image_crc_valid,
    )
