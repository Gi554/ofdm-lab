"""Image RGB paquetisée sur la chaîne OFDM existante ; erreurs observées, sans FEC."""

from dataclasses import dataclass

import numpy as np

from .channels import apply_multipath, frequency_response, impulse_response
from .estimation import (
    PilotLayout,
    estimate_channel_ls,
    pilot_energy_budget,
    receive_pilots,
    transmit_pilots,
)
from .image_transport import (
    HEADER_BYTES,
    ImageReception,
    decode_image,
    encode_image,
    validate_image,
)
from .noise import add_awgn
from .receiver import receive


@dataclass(frozen=True)
class ImageTrial:
    reception: ImageReception
    metrics: dict


def simulate_image(
    image,
    layout: PilotLayout,
    taps,
    ebn0_db,
    seed,
    *,
    estimation="perfect",
    equalizer="zf",
    chunk_bytes=192,
):
    """Frontières de paquets, début et longueur de transport connus du lien physique.

    Le décodeur image ne reçoit que les octets reçus et la taille de bloc publique.
    Les dimensions originales servent uniquement aux mesures, pas à la reconstruction.
    Eb/N0 nominal utilise l'alphabet Es=1 ; l'image non uniforme peut avoir une autre
    énergie réalisée, qui est donc mesurée séparément. None désactive le bruit.
    """
    original = validate_image(image)
    encoded = encode_image(original, chunk_bytes)
    bits = np.unpackbits(np.frombuffer(encoded, dtype=np.uint8), bitorder="big")
    padding = (-bits.size) % layout.bits_per_frame
    padded = np.pad(bits, (0, padding))
    tx = transmit_pilots(padded, layout)
    config = layout.config
    h = impulse_response(taps)
    budget = pilot_energy_budget(layout, 0 if ebn0_db is None else ebn0_db, "total")
    n0 = 0.0 if ebn0_db is None else budget["noise_variance"]
    received = add_awgn(apply_multipath(tx.waveform, h)[: tx.waveform.size], n0, seed)
    if estimation == "perfect":
        response = frequency_response(h, config.n_fft)
    elif estimation == "pilot":
        response = estimate_channel_ls(receive(received, config).grid, layout)
    elif estimation == "none":
        response = None
    else:
        raise ValueError("L'estimation doit être perfect, pilot ou none.")
    if equalizer not in ("zf", "mmse"):
        raise ValueError("L'égaliseur doit être zf ou mmse.")
    decided = receive_pilots(
        received,
        layout,
        channel_response=response,
        equalizer="none" if response is None else equalizer,
        noise_variance=n0,
    )
    received_bits = decided[: bits.size]
    received_bytes = np.packbits(received_bits, bitorder="big").tobytes()
    reception = decode_image(received_bytes, chunk_bytes)
    packet_size = HEADER_BYTES + chunk_bytes
    packets = len(encoded) // packet_size
    raw_payload = []
    header_errors = packet_padding_errors = 0
    source_bytes = np.frombuffer(encoded, dtype=np.uint8)
    result_bytes = np.frombuffer(received_bytes, dtype=np.uint8)
    xor = source_bytes ^ result_bytes
    for index in range(packets):
        start = index * packet_size
        used = min(chunk_bytes, original.size - index * chunk_bytes)
        raw_payload.append(result_bytes[start + HEADER_BYTES : start + HEADER_BYTES + used])
        header_errors += int(np.unpackbits(xor[start : start + HEADER_BYTES]).sum())
        packet_padding_errors += int(
            np.unpackbits(xor[start + HEADER_BYTES + used : start + packet_size]).sum()
        )
    raw = np.concatenate(raw_payload)
    difference = raw ^ original.ravel()
    total_energy = float(np.sum(abs(tx.waveform) ** 2))
    diagnostic_errors = accepted_errors = accepted_corrupt = None
    erased = original.size
    if reception.accepted is not None:
        diagnostic_errors = int(np.count_nonzero(reception.diagnostic != original))
        accepted_errors = int(np.count_nonzero(reception.accepted != original))
        accepted_corrupt = int(
            np.count_nonzero(reception.accepted_bytes & (reception.accepted != original))
        )
        erased = int(original.size - np.count_nonzero(reception.accepted_bytes))
    payload_bit_errors = int(np.unpackbits(difference).sum())
    errors = int(np.count_nonzero(received_bits != bits))
    metrics = dict(
        n_fft=config.n_fft,
        n_active=config.n_active,
        cp_length=config.cp_length,
        order=config.order,
        spacing_hz=config.spacing_hz,
        pilot_spacing=layout.spacing,
        estimation=estimation,
        equalizer="none" if response is None else equalizer,
        channel_taps=[[float(z.real), float(z.imag)] for z in h],
        seed=int(seed),
        ebn0_db=ebn0_db,
        noise_variance=n0,
        energy_reference=(
            "nominal total per OFDM data bit (transport, headers and padding included)"
        ),
        noise_disabled=ebn0_db is None,
        actual_transmitted_energy=total_energy,
        actual_eb_transport=total_energy / padded.size,
        actual_eb_image=total_energy / (original.size * 8),
        n_ofdm_symbols=int(padded.size // layout.bits_per_frame),
        image_width=original.shape[1],
        image_height=original.shape[0],
        image_bytes=int(original.size),
        payload_n_bits=int(original.size * 8),
        payload_bit_errors=payload_bit_errors,
        payload_ber=payload_bit_errors / (original.size * 8),
        raw_payload_byte_errors=int(np.count_nonzero(difference)),
        transport_n_bits=int(bits.size),
        transport_bit_errors=errors,
        transport_ber=errors / bits.size,
        header_bit_errors=header_errors,
        packet_padding_bit_errors=packet_padding_errors,
        ofdm_padding_bits=int(padding),
        ofdm_padding_bit_errors=int(np.count_nonzero(decided[bits.size :])),
        transmitted_packets=packets,
        chunk_bytes=int(chunk_bytes),
        header_bytes_per_packet=HEADER_BYTES,
        packet_padding_bytes=packets * chunk_bytes - original.size,
        expected_packets_rx=reception.expected_packets,
        valid_packets=reception.valid_packets,
        corrupt_payload_packets=reception.corrupt_payload_packets,
        invalid_header_packets=reception.invalid_header_packets,
        missing_packets_rx=reception.missing_packets,
        reconstructed=reception.accepted is not None,
        image_crc_valid=reception.image_crc_valid,
        reconstruction_status=(
            "complete"
            if reception.image_crc_valid is True
            else "partial"
            if reception.valid_packets
            else "metadata_only"
            if reception.accepted is not None
            else "unavailable"
        ),
        diagnostic_byte_errors=diagnostic_errors,
        accepted_byte_errors=accepted_errors,
        erased_bytes=int(erased),
        accepted_corrupt_bytes=accepted_corrupt,
        interval_method="aucun : image déterministe non iid",
        numpy_version=np.__version__,
    )
    return ImageTrial(reception, metrics)
