def patch_delta(base, delta):
    pos = 0
    
    # Read source size
    source_size = 0                             # Example: decoding 300 using Git varint encoding
    shift = 0                                   # 300 (binary) = 1 0010 1100
    while True:                                 # Split into 7-bit chunks (LSB first):
        byte = delta[pos]                       #   0101100 (44), 0000010 (2)
        pos += 1                                # Encoded bytes:
        source_size |= (byte & 0x7f) << shift   #   10101100 (0xAC), 00000010 (0x02)
        shift += 7                              # Decode:
        if not (byte & 0x80): break             #   44 << 0  +  2 << 7  = 300
    
    if source_size != len(base):
        raise Exception("Delta source size mismatch")
        
    # Read target size
    target_size = 0
    shift = 0
    while True:
        byte = delta[pos]
        pos += 1
        target_size |= (byte & 0x7f) << shift
        shift += 7
        if not (byte & 0x80): break
        
    out = bytearray()
    while pos < len(delta):
        byte = delta[pos]
        pos += 1
        
        if byte & 0x80:     # In an 8 byte offset, it stores which bytes are used; same for size
            # Copy command
            offset = 0
            size = 0
            if byte & 0x01: 
                offset = delta[pos]
                pos += 1
            if byte & 0x02:
                offset |= delta[pos] << 8
                pos += 1
            if byte & 0x04:
                offset |= delta[pos] << 16
                pos += 1
            if byte & 0x08:
                offset |= delta[pos] << 24
                pos += 1
                
            if byte & 0x10:
                size = delta[pos]
                pos += 1
            if byte & 0x20:
                size |= delta[pos] << 8
                pos += 1
            if byte & 0x40:
                size |= delta[pos] << 16
                pos += 1
                
            if size == 0: size = 0x10000
            
            if offset + size > len(base):
                raise Exception("Delta copy offset out of bounds")
            
            out.extend(base[offset:offset+size])
        else:
            # Insert command
            size = byte 
            if pos + size > len(delta):
                raise Exception("Delta insert size out of bounds")
            out.extend(delta[pos:pos+size])
            pos += size
            
    if len(out) != target_size:
        raise Exception("Delta target size mismatch")
        
    return bytes(out)