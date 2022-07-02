// endianness.c
// visualizer for big-endian and little-endian storage

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <math.h>
#include <string.h>

typedef unsigned char byte;
typedef char const *const typeName;

typeName INT8 = "int8";
typeName INT16 = "int16";
typeName INT32 = "int32";
typeName INT64 = "int64";
typeName UINT8 = "uint8";
typeName UINT16 = "uint16";
typeName UINT32 = "uint32";
typeName UINT64 = "uint64";

/**
 * @brief Accumulate the bytes into a Little Endian array.
 *
 * @param num The input value to visualize.
 * @param size The number of bytes num occupies.
 * @return char* Pointer to heap-allocated byte array.
 */
byte *getBytes(int64_t num, size_t size)
{
    byte *bytes = (char *)malloc(size);
    size_t extractor = 0xFF;
    for (size_t i = 0; i < size; ++i)
    {
        int64_t extracted = extractor & num;
        byte b = extracted >> (8 * i);
        bytes[i] = b;
        extractor <<= 8;
    }
    return bytes;
}

/**
 * @brief Debugging function for printing an array of bytes.
 *
 * @param array The array to print.
 * @param len The number of elements in the array.
 */
void _printArray(byte *array, size_t len)
{
    if (len < 1)
    {
        printf("[]\n");
        return;
    }
    printf("[");
    for (size_t i = 0; i < len - 1; ++i)
        printf("%lu, ", array[i]);
    printf("%lu]\n", array[len - 1]);
}

size_t numBytes(typeName name)
{
    if (!strcmp(name, INT8))
        return sizeof(int8_t);
    if (!strcmp(name, INT16))
        return sizeof(int16_t);
    if (!strcmp(name, INT32))
        return sizeof(int32_t);
    if (!strcmp(name, INT64))
        return sizeof(int64_t);
    if (!strcmp(name, UINT8))
        return sizeof(uint8_t);
    if (!strcmp(name, UINT16))
        return sizeof(uint16_t);
    if (!strcmp(name, UINT32))
        return sizeof(uint32_t);
    if (!strcmp(name, UINT64))
        return sizeof(uint64_t);
    return 0;
}

void printInfo(typeName type, int64_t input)
{
    size_t size = numBytes(type);
    printf("Type: %s (%lu bytes)\n", type, size);
    size_t extractor = pow(2, size * 8) - 1;
    input = input & extractor;
    printf("Decimal: %d\n", input);
    printf("Hexadecimal: 0x%X\n", input);
}

void printBoundary(size_t size)
{
    printf("+");
    for (size_t i = 0; i < size - 1; ++i)
        printf("------+");
    printf("------+\n");
}

void printBoxes(size_t num, size_t size)
{
    byte *bytes = getBytes(num, size);

    printf("Little Endian:\n");

    printBoundary(size);
    printf("|");
    for (size_t i = 0; i < size; ++i)
        printf(" 0x%.2X |", bytes[i]);
    printf("\n");
    printBoundary(size);

    printf("Big Endian:\n");

    printBoundary(size);
    printf("|");
    for (size_t i = size; i > 0; --i)
        printf(" 0x%.2X |", bytes[i - 1]);
    printf("\n");
    printBoundary(size);

    free(bytes);
}

int64_t S64(char const *s)
{
    int64_t i;
    char c;
    int scanned = sscanf(s, "%" SCNd64 "%c", &i, &c);
    return (scanned >= 1) ? i : 0;
}

int main(int argc, char const *argv[])
{
    /*
    INPUT:
        ./endianness int 309
    OUTPUT:
        Type: int (4 bytes)
        Decimal: 309
        Hexadecimal: 0x135
        Little Endian:
        +------+------+------+------+
        | 0x35 | 0x01 | 0x00 | 0x00 |
        +------+------+------+------+
        Big Endian:
        +------+------+------+------+
        | 0x00 | 0x00 | 0x01 | 0x35 |
        +------+------+------+------+
    */
    if (argc < 3)
    {
        printf("Insufficient arguments! Usage: ./endianness <type> <value>\n");
        printf("Example: ./endianness int 309\n");
        printf("Available data types: int8, int16, int32, int64, uint8, uint16, uint32, uint64\n");
        return EXIT_FAILURE;
    }
    typeName type = argv[1];
    int64_t const input = S64(argv[2]);

    printInfo(type, input);
    printBoxes(input, numBytes(type));

    return EXIT_SUCCESS;
}
