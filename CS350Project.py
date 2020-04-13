from pyeda.inter import *
from pyeda.boolalg.boolfunc import *
from IPython.display import SVG, display
from gvmagic import *

def outEdge1(x):
    return ((x+3) % 32)

def outEdge2(x):
    return ((x+8) % 32)

def buildGraphEdges(IntNodes):
    print("Getting all node egdes...")
    IntEdges = []
    for i in IntNodes:
        pair1 = (i, outEdge1(i))
        pair2 = (i, outEdge2(i))
        IntEdges.append( pair1 )
        IntEdges.append( pair2 )
        print("\t Node ", i, " edges: \t", pair1, "\t" , pair2)
    print("\nAll node edges gathered!\n")
    return IntEdges

def convertNumberToBoolExpression(num):
    # num2point is in little-endian, thus x4 = 1's place bit.
    bits = num2point(num, "i[4] i[3] i[2] i[1] i[0]".split())
    newFormula = "("
    for key, value in bits.items(): # Convert each bit into a boolean formula
        newFormula += (("" if (value == 1) else "~") + key + " & ")
    # trim the trailing " & ", and return the string.
    newFormula = newFormula[:-3] + ")"
    print("\t", newFormula)
    return newFormula

def buildNodeExpression(IntNodes):
    print("Building all node expressions...\n")
    # Encode all nodes numbers into 5 bit representations.
    BinNodes = {}
    for i in IntNodes:
        BinNodes[i] = convertNumberToBoolExpression(i)
    
    print("\nAll node expressions gathered!\n")
    return BinNodes

def buildEdgeExpression(BinNodes, IntEdges):
    # buildNodeExpressionStrings() and buildGraphEdges() must be ran before this.
    # Takes each edge tuple in IntEdges, and finds their expression string in BinEdges
    # Then, it replaces i's with xs and ys, respectively
    print("Building all edge expressions...\n")
    BinEdges = []
    for x, y in IntEdges:
        xFormula = BinNodes[x].replace("i", "x")
        yFormula = BinNodes[y].replace("i", "y")
        tempFormula = "(" + xFormula +  "&" + yFormula + ")"
        BinEdges.append(tempFormula)
        print("\t", tempFormula)
    print("\nAll graph expressions gathered!\n")
    return BinEdges

def buildGraphExpression(BinEdges):
    # Pretty easy, just itterating through each edge expression we've already built,
    # and Or-ing them all together to create our full graph.
    print("Building graph expression...\n")
    graphFormulaString = ""
    for expression in BinEdges:
        graphFormulaString += expression + " | "
    graphFormulaString = graphFormulaString[:-3]
    print("\tGraph Formula: ", graphFormulaString, "\nGraph expression built!\n")
    return graphFormulaString

def buildPrimeToEvenGraphExpression(BinNodes, IntPrimes):
    graphFormulaString = ""
    print("Building prime to even graph expression...\n")
    for i in IntPrimes:
        # First add the boolean expression for the prime,
        # then we And with ~y[4] to remove any non-even value from the graph.
        # (bit y[4] = 1s place, which is always == 0 for even numbers)
        # finally, we add an Or to add all primes to this graph.
        graphFormulaString += "(" + BinNodes[i].replace("i", "x") + " & (~y[4])) | "
    graphFormulaString = graphFormulaString[:-3]
    print("\tGraph Formula: ", graphFormulaString, "\n\nPrime to Even Graph expression built!\n")
    return graphFormulaString

def buildUniquePairGraphExpression(BinNodes, IntPrime, IntEven):
    print("Building given pair Prime to Even graph expression...\n")
    graphFormulaString  = "(" + BinNodes[IntPrime].replace("i", "x") + " & " + BinNodes[IntEven].replace("i", "y") + ")";
    print("\tGraph Formula: ", graphFormulaString, "\n\nPrime to Even Graph expression built!\n")
    return graphFormulaString

def computeRComposeR(BDDGraph):
    print("Composing Graph...")
    x0, x1, x2, x3, x4 = bddvars("x", 5)
    y0, y1, y2, y3, y4 = bddvars("y", 5)
    z0, z1, z2, z3, z4 = bddvars("z", 5)

    R1 = BDDGraph.compose({y0:z0, y1:z1, y2:z2, y3:z3, y4:z4 })
    R2 = BDDGraph.compose({x0:z0, x1:z1, x2:z2, x3:z3, x4:z4 })
    RComposeR = (R1 & R2).smoothing((z0, z1, z2, z3, z4))
    print("Graph RR composed!\n")
    return RComposeR

def computeTransitiveClosure(R):
    print("Calculating transitive closure...")
    x0, x1, x2, x3, x4 = bddvars("x", 5)
    y0, y1, y2, y3, y4 = bddvars("y", 5)
    z0, z1, z2, z3, z4 = bddvars("z", 5)

    H = R
    while (True):
        HPrime = H
        # 
        Hi = HPrime.compose({y0:z0, y1:z1, y2:z2, y3:z3, y4:z4})
        Ri = R.compose({x0:z0, x1:z1, x2:z2, x3:z3, x4:z4})
        # Calculate new H graph, and
        # Remove z-substitutions from the graph
        H = (HPrime | (Hi & Ri)).smoothing((z0, z1, z2, z3, z4))

        if (H.equivalent(HPrime)):
            # We've found the transitive closure
            # short circuit, and return H
            print("Calculated!\n")
            return H

def runForAll():
    print("Calculating if all Odd Prime Nodes in a 32 node graph from 0 to 31 they can reach some Even Node in an even number of steps...\n")
    #create the bdd vars that we later use to remove the substitute nodes in the graph
    x0, x1, x2, x3, x4 = bddvars("x", 5)
    y0, y1, y2, y3, y4 = bddvars("y", 5)

    # Defining the initial sets of numbers
    intNodes = [i for i in range(0, 32)]
    intEvens = [i for i in range(0, 32, 2)]
    intPrimes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    
    # building the edges between nodes as tuples of (i, j)
    intEdges = buildGraphEdges(intNodes)

    # build boolean expressions for all nodes
    binNodes = buildNodeExpression(intNodes)

    # build boolean expressions for all edges
    binEdges = buildEdgeExpression(binNodes, intEdges)

    # build the boolean expression for the entire graph
    binGraphExpression = buildGraphExpression(binEdges)
    
    # build boolean expressions for the prime->even graph
    binPrimeToEvenExpression = buildPrimeToEvenGraphExpression(binNodes, intPrimes)
    
    # get the BDDs from the expressions
    binGraphBDD = expr2bdd(expr(binGraphExpression))
    binPrimeToEvenBDD = expr2bdd(expr(binPrimeToEvenExpression))

    # Build a transposed graph of all nodes that are.
    RR2 = computeRComposeR(binGraphBDD)
    # fully transposed graph of evenly spaced nodes
    RR2Star = computeTransitiveClosure(RR2)
    print("Calculating final BDD graph...")
    PE = (RR2Star & binPrimeToEvenBDD).smoothing((x0, x1, x2, x3, x4, y0, y1, y2, y3, y4))
    print("It's done!!!\n")
    return PE

def runForUnique(prime, even):
    print("Calculating if Prime Node ", prime, " can reach Even Node ", even, " in an even number of steps...")

    # Defining the initial sets of numbers
    intNodes = [i for i in range(0, 32)]
    intEvens = [i for i in range(0, 32, 2)]
    intPrimes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    
    if ((prime not in intPrimes) or (even not in intEvens)):
        print("Error: value out of bounds.")
        return None
    
    #create the bdd vars that we later use to remove the substitute nodes in the graph
    x0, x1, x2, x3, x4 = bddvars("x", 5)
    y0, y1, y2, y3, y4 = bddvars("y", 5)
    
    # building the edges between nodes as tuples of (i, j)
    intEdges = buildGraphEdges(intNodes)

    # build boolean expressions for all nodes
    binNodes = buildNodeExpression(intNodes)

    # build boolean expressions for all edges
    binEdges = buildEdgeExpression(binNodes, intEdges)

    # build the boolean expression for the entire graph
    binGraphExpression = buildGraphExpression(binEdges)
    
    # build the graph expression for the unique pair of prime and even nodes
    binUniquePairExpression = buildUniquePairGraphExpression(binNodes, prime, even)
    
    # convert the expressions to BDDs
    binGraph = expr2bdd(expr(binGraphExpression))
    binUniquePairGraph = expr2bdd(expr(binUniquePairExpression))

    # Build a transposed graph of all nodes that are 2 steps from one another
    RR2 = computeRComposeR(binGraph)
    # fully transposed graph of all evenly spaced nodes.
    RR2Star = computeTransitiveClosure(RR2)
    print("Calculating final BDD graph...")
    PE = (RR2Star & binUniquePairGraph).smoothing((x0, x1, x2, x3, x4, y0, y1, y2, y3, y4))
    print("It's done!!!\n")
    return PE

if __name__ == '__main__':
    graphAll = runForAll().equivalent(True)
    graphUnique = runForUnique(5, 8).equivalent(True)

    print("\n\n\n**********************************************************************************************")
    print("\tWith a graph of 32 nodes labeled from 0 to 31, where every node i connects to both the (i+3)%32th and (i+8)%32th nodes, is it true that all prime nodes > 2, have a walk to an even node in an even number of steps?\n\tIt is :", graphAll)
    print("\tWith a graph of 32 nodes labeled from 0 to 31, where every node i connects to both the (i+3)%32th and (i+8)%32th nodes, is it true that some prime node, say 5, has a walk to an even node, say 8, in an even number of steps?\n\tIt is :", graphUnique)
    