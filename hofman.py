# bit array, ale bez encode w celach edukacyjnych
from bitarray import bitarray
from numpy import log2
from math import ceil
import os

def create_frequency_dictionary(text : str):
    frequency_dictionary = {}
    frequency_dictionary['🏁'] = 0  # Dodajemy znak końca
    for char in text:
        if char not in frequency_dictionary:
            frequency_dictionary[char] = 0
        frequency_dictionary[char] += 1
    return frequency_dictionary

def validate_texts(text1 : str, text2 : str):
    if text1 == text2:
        return True
    return False

class hofmanNode:
    def __init__(self, key, freq):
        self.key = key
        self.freq = freq
        self.left = None
        self.right = None

    def add(self, node):
        if node.freq < self.freq:
            self.right = self.copy()
            self.left = node
            self.freq += node.freq
            self.key += node.key
        else:
            self.left = self.copy()
            self.right = node
            self.freq += node.freq
            self.key += node.key

    def copy(self):
        new_node = hofmanNode(self.key, self.freq)
        new_node.left = self.left
        new_node.right = self.right
        return new_node
    
    def print(self): # test
        print(f"Node: {self.key}, Frequency: {self.freq}")
        if self.left:
            print("Left child:")
            self.left.print()
        if self.right:
            print("Right child:")
            self.right.print()

    def makeCode(self, codeOriginal = None, codes = {}):
        if self.left is None and self.right is None:
            code = codeOriginal.copy()
            if code is None:
                code = bitarray('0')
            codes[self.key] = code
        if self.left:
            if codeOriginal is None:
                code = bitarray('0')
            else:
                code = code = codeOriginal.copy() + bitarray('0')
            code = self.left.makeCode(codeOriginal = code, codes = codes)
        if self.right:
            if codeOriginal is None:
                code = bitarray('1')
            else:
                code = codeOriginal.copy() + bitarray('1')
            code = self.right.makeCode(codeOriginal = code, codes = codes)
        return code


class BinaryCoding:
    def __init__(self):
        self._n = 0
        self._code = {}
        print("Well Done, I've created a BinaryCoding object")

    def get_code(self):
        return self._code

    def _fq_dictonary_to_codebook(self, frequency_dictionary : dict):
        if '🏁' not in frequency_dictionary:
            raise ValueError("No end character in frequency dictionary, try to use create_frequency_dictionary")
        
        self._n = ceil(log2(len(frequency_dictionary)))
        self._code = {}

        for i, key in enumerate(frequency_dictionary):
            code = bitarray(format(i, f'0{self._n}b'))
            self._code[key] = code

    def _fq_dictonary_to_hofman_codebook(self, frequency_dictionary : dict):
        hofman_dictionary = frequency_dictionary.copy()
        roots = {}

        while len(hofman_dictionary) > 1:
                    minKey = min(hofman_dictionary, key=hofman_dictionary.get)
                    minValue = hofman_dictionary[minKey]
                    hofman_dictionary.pop(minKey)

                    minKey2 = min(hofman_dictionary, key=hofman_dictionary.get)
                    minValue2 = hofman_dictionary[minKey2]
                    hofman_dictionary.pop(minKey2)

                    if minKey not in roots:
                        minKeyNode = hofmanNode(minKey, minValue)
                    else:
                        minKeyNode = roots[minKey]
                        roots.pop(minKey)

                    if minKey2 not in roots:
                        minKey2Node = hofmanNode(minKey2, minValue2)
                    else:
                        minKey2Node = roots[minKey2]
                        roots.pop(minKey2)

                    minKeyNode.add(minKey2Node)            

                    newKey = minKey + minKey2
                    newValue = minValue + minValue2

                    roots[newKey] = minKeyNode
                    hofman_dictionary[newKey] = newValue

        codes = {}
        root = roots.popitem()
        root = root[1]

        root.makeCode(codes = codes)
        self._code = codes


    def create(self, frequency_dictionary : dict = None, text : str = None, hofman : bool = False):
        if hofman:
            if frequency_dictionary is None and text is None:
                raise ValueError("Either frequency_dictionary or text must be provided")
            
            if frequency_dictionary is not None:
                self._fq_dictonary_to_hofman_codebook(frequency_dictionary)
            if text is not None:
                frequency_dictionary = create_frequency_dictionary(text)
                self._fq_dictonary_to_hofman_codebook(frequency_dictionary)
            return
        else:
            if frequency_dictionary is None and text is None:
                raise ValueError("Either frequency_dictionary or text must be provided")
            
            if frequency_dictionary is not None:
                self._fq_dictonary_to_codebook(frequency_dictionary)
            if text is not None:
                frequency_dictionary = create_frequency_dictionary(text)
                self._fq_dictonary_to_codebook(frequency_dictionary)

    def change_code(self, code : dict):
        if not isinstance(code, dict):
            raise ValueError("Code must be a dictionary")
        if '🏁' not in code:
            raise ValueError("Code must contain end character '🏁'")
        self._code = code
        self._n = ceil(log2(len(code)))

    def encode(self, text : str):
        if '🏁' not in text:
            text += '🏁'

        encoded = bitarray()
        for char in text:
            if char in self._code:
                encoded.extend(self._code[char])
            else:
                raise ValueError(f"Character {char} not in codebook")
        return encoded

    def decode(self, coded_text : bitarray):
        decoded = ""
        i = 0
        while i < len(coded_text):
            for key, code in self._code.items():
                if coded_text[i:i+len(code)] == code:
                    if key == "🏁":
                        return decoded
                    decoded += key
                    i += len(code)
                    break
        return decoded
    
    def save(self, coded_text: bitarray, path: str):
        with open(path, 'wb') as file:
            for char in self._code.keys():
                file.write(char.encode('utf-8'))
            file.write(b'\n')  # separator po znakach

            for char in self._code.keys():
                char_len = len(self._code[char])
                file.write(char_len.to_bytes(4, 'big'))  # zapis długości jako bajty

            codes_line = bitarray()
            for char in self._code.keys():
                codes_line += self._code[char]

            codes_and_coded_text = codes_line + coded_text
            codes_and_coded_text.tofile(file)

    def load(self, path: str):
        with open(path, 'rb') as file:
            chars = file.readline().decode('utf-8')
            chars = chars.strip('\n')

            lengths_raw = file.read(4 * len(chars))  # czytamy wszystkie długości

            code_lengths = []
            for i in range(len(chars)):
                char_len_bytes = lengths_raw[i*4:(i+1)*4]
                char_len = int.from_bytes(char_len_bytes, 'big')
                code_lengths.append(char_len)

            codes_line = bitarray()
            codes_line.fromfile(file)

            codes_from_file = []
            pointer = 0
            for length in code_lengths:
                code = codes_line[pointer:pointer+length]
                codes_from_file.append(code)
                pointer += length

            code = {chars[i]: codes_from_file[i] for i in range(len(chars))}
            encoded_text = codes_line[pointer:]

        return code, encoded_text


# Example usage        
with open('norm_wiki_sample.txt', 'r') as file:
    text = file.read()

bc = BinaryCoding()
bc.create(text = text, hofman = True)
encoded = bc.encode(text)
path = 'encoded_hofman.bin'
bc.save(encoded, path)
code_lengths = []
code = bc.get_code()
for key, value in code.items():
    code_lengths.append(len(value))
print(code_lengths)

# # decodowanie trwa dość długo
# decoded = bc.decode(coded_text)
# print("Decoded text is the same as original:", validate_texts(text, decoded)) 

original_size = os.path.getsize('norm_wiki_sample.txt')
encoded_size = os.path.getsize(path)
print(f"Original size: {original_size} bytes")
print(f"Encoded size: {encoded_size} bytes")
print(f"Compression ratio (original/encoded): {original_size / encoded_size:.2f}")
print(f"Compression difrence (original - encoded): {original_size - encoded_size} bytes")

code, encoded_text = bc.load(path)
bc.change_code(code)
decoded = bc.decode(encoded_text)
print("Decoded text is the same as original:", validate_texts(text, decoded))
