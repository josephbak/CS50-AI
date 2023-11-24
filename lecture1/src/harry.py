from logic import *

rain = Symbol("rain") # It is raining.
hagrid = Symbol("hagrid") # Harry visited Hagrid.
dumbledore = Symbol("dumbledore") # Harry visited Dumblerdore.

knowledge = And(
    Implication(Not(rain), hagrid), # If it wasn't raining, Harry visited Hagrid.
    Or(hagrid, dumbledore), # Harry visited one of Hagrid and Dumbledore.
    Not(And(hagrid, dumbledore)), # Harry visited one of Hagrid and Dumbledore.
    dumbledore # Harry visited Dumbledore.
)

print(model_check(knowledge, rain))
