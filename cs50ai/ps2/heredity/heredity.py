import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def gene_counter(person, one_gene, two_genes):
    if person in one_gene:
        return 1
    elif person in two_genes:
        return 2
    else:
        return 0


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """ 


    def p_parent_pass_gene_on(parent_count):
        if parent_count in (1,2):
            return 0.5 * parent_count * (1 - PROBS['mutation'])
        elif parent_count == 0:
            return PROBS['mutation']
        else:
            raise ValueError('parent_count is unexpected value: %s' % parent_count)

    #is_right_joint = (one_gene == {"Harry"} and two_genes=={'James'} and have_trait == {'James'})

    current_joint_p = 1
    for person in people:
        person_genecount = gene_counter(person,one_gene,two_genes)

        # case when no parent information
        if people[person]['father'] is None or people[person]['mother'] is None:
            p_genecount = PROBS['gene'][person_genecount]
        else:
            father_count = gene_counter(people[person]['father'],one_gene,two_genes)
            mother_count = gene_counter(people[person]['mother'],one_gene,two_genes)

            # now compute how likely this person is to end up with the gene count given parent gene counts:
            if person_genecount == 0:
                p_genecount = (1 - p_parent_pass_gene_on(father_count)) * (1 - p_parent_pass_gene_on(mother_count))
            elif person_genecount == 1:
                p_genecount = ((p_parent_pass_gene_on(father_count)) * (1 - p_parent_pass_gene_on(mother_count))) + ((1 - p_parent_pass_gene_on(father_count)) * (p_parent_pass_gene_on(mother_count)))
            elif person_genecount == 2:
                p_genecount = (p_parent_pass_gene_on(father_count)) * (p_parent_pass_gene_on(mother_count))
            else:
                raise ValueError('person_genecount is unexpected value: %s' % person_genecount)
        
        this_setting_prob = PROBS['trait'][person_genecount][person in have_trait] * p_genecount

        # multiply to get current joint probability
        current_joint_p = current_joint_p * this_setting_prob

    #     if is_right_joint and person == 'Harry' and person_genecount == 1:
    #         print(this_setting_prob)
    #         print(p_parent_pass_gene_on(father_count))
    #         print(p_parent_pass_gene_on(mother_count))
    #         print(p_genecount)    
    # if is_right_joint:    
    #     print(current_joint_p)

    return current_joint_p


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        person_count = gene_counter(person, one_gene, two_genes)
        probabilities[person]['gene'][person_count] = probabilities[person]['gene'][person_count] + p
        probabilities[person]['trait'][person in have_trait] = probabilities[person]['trait'][person in have_trait] + p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        for p_subject in ['gene','trait']:
            p_sum = 0
            for value in probabilities[person][p_subject]:
                p_sum = p_sum + probabilities[person][p_subject][value]
            for value in probabilities[person][p_subject]:
                probabilities[person][p_subject][value] = probabilities[person][p_subject][value] / p_sum




if __name__ == "__main__":
    main()
