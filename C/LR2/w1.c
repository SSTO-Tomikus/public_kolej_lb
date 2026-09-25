#include <stdio.h>
#include <math.h>
#include <string.h>

const int variant_number = 23;
int group_number = 79;
const float PI = 3.14;
double suma = variant_number + PI;
int suma_conv = variant_number + PI;

const int NAME_NUMBER = 6;

int main() {
    printf("My jornal nomber %d. His Cos = %f\n", variant_number, cos(variant_number));
    char name[] = "Sergii";
    printf("Group: %d, Variant: %d, Name: %s\n", group_number, variant_number, name);
    printf("Sum: %d.\n Sum whis convertion: %f\n", suma_conv, suma);
}

