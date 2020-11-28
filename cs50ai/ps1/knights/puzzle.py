from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # A must be Knight or Knave
    # A not Knight and Knave
    Or(AKnight,AKnave)
    ,Not(And(AKnight,AKnave))
    # A says “I am both a knight and a knave.”
    # StatementA: = And(AKnight,AKnave)
    # either A is a Knight in which case the statement is true, or A is a Knave and the statement is false.
    ,Or(And(AKnight,And(AKnight,AKnave)), And(AKnave,Not(And(AKnight,AKnave))))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # A must be Knight or Knave
    # A not Knight and Knave
    Or(AKnight,AKnave)
    ,Not(And(AKnight,AKnave))   
    # B must be Knight or Knave
    # B not Knight and Knave
    ,Or(BKnight,BKnave)
    ,Not(And(BKnight,BKnave)) 
    # A says “We are both knaves.”
    # StatementA: AND(AKnave,BKnave)
    # either A is a Knight in which case statement A is true, or A is a Knave and statementA is false
    ,Or(And(AKnight,And(AKnave,BKnave)), And(AKnave,Not(And(AKnave,BKnave))))
)
#check puzzle 1.
# if AKnave and BKnave, then AKnight, contradiction
# if AKnave and BKnight, no contradiction
# if AKnight and BKnight, then AKnave, contradiction
# if AKnight and BKnave, then AKnave, contradiction

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # A must be Knight or Knave
    # A not Knight and Knave
    Or(AKnight,AKnave)
    ,Not(And(AKnight,AKnave))   
    # B must be Knight or Knave
    # B not Knight and Knave
    ,Or(BKnight,BKnave)
    ,Not(And(BKnight,BKnave)) 
    # A says "We are the same kind."
    # StatementA: Or(And(AKnight,BKnight),And(AKnave,BKnave))
    ,Or(And(AKnight,Or(And(AKnight,BKnight),And(AKnave,BKnave))),And(AKnave,Not(Or(And(AKnight,BKnight),And(AKnave,BKnave)))))
    # B says "We are of different kinds."
    # StatementB: Or(And(AKnight,BKnave),And(AKnave,BKnight))
    ,Or(And(BKnight,Or(And(AKnight,BKnave),And(AKnave,BKnight))),And(BKnave,Not(Or(And(AKnight,BKnave),And(AKnave,BKnight)))))
)
#check puzzle 2.
# if AKnave and BKnave, then AKnight, contradiction
# if AKnave and BKnight, no contradiction
# if AKnight and BKnight, then AKnave, contradiction
# if AKnight and BKnave, then AKnave, contradiction

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # A must be Knight or Knave
    # A not Knight and Knave
    Or(AKnight,AKnave)
    ,Not(And(AKnight,AKnave))   
    # B must be Knight or Knave
    # B not Knight and Knave
    ,Or(BKnight,BKnave)
    ,Not(And(BKnight,BKnave)) 
    # C must be Knight or Knave
    # C not Knight and Knave
    ,Or(CKnight,CKnave)
    ,Not(And(CKnight,CKnave))   
    # A says either "I am a knight." or "I am a knave.", but you don't know which
    # SituationA1: Or(And(AKnight,AKnight), And(AKnave,Not(AKnight)))
    # SituationA2: Or(And(AKnight,AKnave), And(AKnave,Not(AKnave)))
    ,Or(Or(And(AKnight,AKnight), And(AKnave,Not(AKnight))), Or(And(AKnight,AKnave), And(AKnave,Not(AKnave))))
    # B says "A said 'I am a knave'."
    # either B is a Knight and A said I am a Knave
    # or B is a Knave and A did not say he is a Knave
    ,Or(And(BKnight,Or(And(AKnight,AKnave), And(AKnave,Not(AKnave)))), And(BKnave, Not(Or(And(AKnight,AKnave), And(AKnave,Not(AKnave))))))
    # B says "C is a knave."
    # either B is a Knight and CKnave
    # or B is a Knave and CKnight
    ,Or(And(BKnight,CKnave), And(BKnave, Not(CKnave)))
    # C says "A is a knight."
    ,Or(And(CKnight,AKnight), And(CKnave,Not(AKnight)))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
