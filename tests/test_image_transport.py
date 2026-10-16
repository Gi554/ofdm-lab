import struct
import zlib

import numpy as np
import pytest

from ofdm_lab.image_transport import (
    HEADER_BYTES,
    decode_image,
    encode_image,
    load_image,
    save_image,
)


def image():
    return np.arange(5 * 7 * 3, dtype=np.uint8).reshape(5, 7, 3)


@pytest.mark.parametrize("chunk", [3, 24, 192])
def test_roundtrip_rgb_dimensions_padding_and_png(tmp_path, chunk):
    original = image()
    encoded = encode_image(original, chunk)
    result = decode_image(encoded, chunk)
    assert np.array_equal(result.accepted, original)
    assert result.valid_packets == (original.size + chunk - 1) // chunk
    assert result.missing_packets == 0
    assert result.corrupt_payload_packets == 0
    assert result.accepted_bytes.all()
    assert result.image_crc_valid is True
    path = tmp_path / "roundtrip.png"
    save_image(path, result.accepted)
    assert np.array_equal(load_image(path), original)


def test_corrupt_payload_is_visible_diagnostically_but_not_accepted():
    encoded = bytearray(encode_image(image(), 24))
    encoded[HEADER_BYTES + 2] ^= 1
    result = decode_image(bytes(encoded), 24)
    assert result.corrupt_payload_packets == 1
    assert result.valid_packets == 4
    assert result.diagnostic[0, 0, 2] == (image()[0, 0, 2] ^ 1)
    assert np.array_equal(result.accepted.reshape(-1, 3)[:8], np.tile([255, 0, 255], (8, 1)))
    assert not result.accepted_bytes.ravel()[:24].any()


def test_header_error_drop_reorder_and_truncation():
    encoded = encode_image(image(), 24)
    size = HEADER_BYTES + 24
    packets = [encoded[i : i + size] for i in range(0, len(encoded), size)]
    assert np.array_equal(decode_image(b"".join(packets[::-1]), 24).accepted, image())
    damaged = bytearray(packets[0])
    damaged[8] ^= 1
    result = decode_image(bytes(damaged) + b"".join(packets[1:]), 24)
    assert result.invalid_header_packets == 1
    assert result.missing_packets == 1
    # Dimensions récupérées uniquement dans les autres en-têtes répétés.
    assert result.accepted.shape == image().shape
    result = decode_image(b"".join(packets[:-1]) + packets[-1][:10], 24)
    assert result.missing_packets == 1
    assert result.truncated_bytes == 10
    assert decode_image(b"", 24).accepted is None
    assert decode_image(bytes(size), 24).accepted is None
    with pytest.raises(ValueError):
        decode_image(encoded + packets[0], 24)


def test_semantically_invalid_header_rejected_even_with_valid_crc():
    encoded = bytearray(encode_image(image(), 24))
    encoded[4] = 99
    encoded[HEADER_BYTES - 4 : HEADER_BYTES] = struct.pack(
        ">I", zlib.crc32(encoded[: HEADER_BYTES - 4])
    )
    result = decode_image(bytes(encoded[: HEADER_BYTES + 24]), 24)
    assert result.accepted is None
    assert result.invalid_header_packets == 1


def test_mixed_images_rejected():
    first = encode_image(image(), 192)
    second = encode_image(np.zeros((4, 4, 3), dtype=np.uint8), 192)
    with pytest.raises(ValueError):
        decode_image(first + second)


@pytest.mark.parametrize(
    "value",
    [np.zeros((0, 3, 3), dtype=np.uint8), np.zeros((3, 3)), np.zeros((2, 2, 4), dtype=np.uint8)],
)
def test_invalid_images(value):
    with pytest.raises(ValueError):
        encode_image(value)


@pytest.mark.parametrize("chunk", [0, 1, 4, 65538, True])
def test_invalid_chunks(chunk):
    with pytest.raises(ValueError):
        encode_image(image(), chunk)


def test_packet_padding_is_outside_pixel_crc():
    encoded = bytearray(encode_image(image(), 192))
    encoded[-1] ^= 1
    result = decode_image(bytes(encoded), 192)
    assert np.array_equal(result.accepted, image())
    assert result.image_crc_valid is True


def test_same_geometry_different_images_rejected():
    a = encode_image(image(), 24)
    b = encode_image(255 - image(), 24)
    size = HEADER_BYTES + 24
    with pytest.raises(ValueError):
        decode_image(a[:size] + b[size:], 24)


def test_png_alpha_composited_on_white(tmp_path):
    import matplotlib.image as mpimg

    pixels = np.array([[[1.0, 0, 0, 0], [0, 0, 1, 1]]])
    path = tmp_path / "alpha.png"
    mpimg.imsave(path, pixels)
    assert np.array_equal(
        load_image(path), np.array([[[255, 255, 255], [0, 0, 255]]], dtype=np.uint8)
    )


def test_png_grayscale_converted_to_rgb(tmp_path):
    import matplotlib.image as mpimg

    path = tmp_path / "gray.png"
    mpimg.imsave(path, np.array([[0.0, 1.0]]), cmap="gray", vmin=0, vmax=1)
    assert np.array_equal(
        load_image(path), np.array([[[0, 0, 0], [255, 255, 255]]], dtype=np.uint8)
    )


def test_complete_image_global_crc_checked():
    encoded = bytearray(encode_image(image(), 192))
    encoded[28] ^= 1
    encoded[HEADER_BYTES - 4 : HEADER_BYTES] = struct.pack(
        ">I", zlib.crc32(encoded[: HEADER_BYTES - 4])
    )
    with pytest.raises(ValueError, match="CRC global"):
        decode_image(bytes(encoded), 192)
