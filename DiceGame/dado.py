import random as Random

entrada = int(input("Cantidad de iteraciones: "))

for i in range(entrada):
    resultado = Random.randint(1, 6)
    print(f"{i + 1} - El resultado del dado es: {resultado}")

print("Resultado de la ultima tirada: ", resultado)