# Python---Hofman-Encoding
**Python - Hofman Encoding with Saving and Loading From File**

This project is part of the "Theory of Information and Data Compression Methods" laboratory.

✅ Supports both Huffman and fixed-length binary encoding
✅ Encodes and decodes any string with a custom alphabet
✅ Automatically appends an end-of-text symbol (🏁)
✅ Saves compressed data and encoding dictionary to a binary file
✅ Loads compressed data and dictionary from file
✅ Verifies decoding correctness
✅ Reports compression ratio and space savings

**🛠️ Requirements**
pip install bitarray
pip install bitarray numpy

**🧠 How It Works**
A frequency dictionary is created from the input text.
A Huffman tree or fixed-length binary codebook is built from the frequency dictionary.
Text is encoded into a compact bitarray using the generated codebook.
The encoded bitarray and codebook are written to a binary file.
The file can be loaded later, restoring both the codebook and encoded text.
The encoded data is decoded back into the original text for verification.

**🧪 Example Usage**
<pre> ```
with open('norm_wiki_sample.txt', 'r') as file:
    text = file.read()

# Create encoder and generate Huffman codebook
bc = BinaryCoding()
bc.create(text=text, hofman=True)

# Encode and save
encoded = bc.encode(text)
path = 'encoded_hofman.bin'
bc.save(encoded, path)

# Show code lengths
print("Code lengths:", [len(code) for code in bc.get_code().values()])

# File sizes
original_size = os.path.getsize('norm_wiki_sample.txt')
encoded_size = os.path.getsize(path)
print(f"Original size: {original_size} bytes")
print(f"Encoded size: {encoded_size} bytes")
print(f"Compression ratio: {original_size / encoded_size:.2f}")
print(f"Bytes saved: {original_size - encoded_size}")

# Load and decode
code, encoded_text = bc.load(path)
bc.change_code(code)
decoded = bc.decode(encoded_text)
print("Decoded matches original:", validate_texts(text, decoded))
 ``` </pre>

**📂 File Format**
The saved .bin file contains:
Encoded characters (UTF-8)
Code lengths (4 bytes per character)
Binary codes concatenated
Encoded message (bitarray)

**📌 Notes**
All encoded strings include a special end character (🏁) to mark termination.
Decoding relies on matching bit patterns, so the codebook must be preserved.
The decode() function stops at the end character, ensuring accurate output.

**📃 License**
This project is provided for educational purposes and under open-source use.

