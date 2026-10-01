"""Decoded string of every vocabulary token (byte-level BPE -> raw bytes -> latin-1 str, so each byte is one char;
ASCII is exact, non-ASCII bytes become chars >= 0x80 which the automaton treats as neutral separators)."""


def _byte_decoder():
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
    cs = bs[:]; n = 0
    for b in range(256):
        if b not in bs: bs.append(b); cs.append(256 + n); n += 1
    return {chr(c): b for b, c in zip(bs, cs)}


def token_strings(hf_tok):
    """Returns (strs, special) where strs[i] is token i's text and special is the set of added/special token ids."""
    bd = _byte_decoder()
    V = max(len(hf_tok), max(hf_tok.get_vocab().values()) + 1)
    special = set(hf_tok.all_special_ids) | {i for i in hf_tok.added_tokens_decoder}
    strs = [""] * V
    for t, i in hf_tok.get_vocab().items():
        if i in special: strs[i] = t; continue
        try: strs[i] = bytes(bd[c] for c in t).decode("latin-1")
        except KeyError: strs[i] = t
    return strs, special
