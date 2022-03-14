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
    prob = 1
    people_with_parents = {}
    for person in people:
        if people[person]['mother'] is not None:
            people_with_parents[person] = {
                "name": people[person]["name"],
                "father_gene": num_of_genes(people[person]["father"], one_gene, two_genes),
                "mother_gene": num_of_genes(people[person]["mother"], one_gene, two_genes), 
            }
    for person in people:
        if person in one_gene:
            if people[person]["mother"] is None: # no parent information
                prob = prob*PROBS["gene"][1]
            else:
                prob = prob*child_gene_probability(1, people_with_parents[person]['father_gene'], people_with_parents[person]['mother_gene'])
            if person in have_trait:
                prob = prob*PROBS["trait"][1][True]
            else:
                prob = prob*PROBS["trait"][1][False]
        elif person in two_genes:
            if people[person]["mother"] is None:
                prob = prob*PROBS["gene"][2]
            else:
                prob = prob*child_gene_probability(2, people_with_parents[person]['father_gene'], people_with_parents[person]['mother_gene'])
            if person in have_trait:
                prob = prob*PROBS["trait"][2][True]
            else:
                prob = prob*PROBS["trait"][2][False]
        else:
            if people[person]["mother"] is None:
                prob = prob*PROBS["gene"][0]
            else:
                prob = prob*child_gene_probability(0, people_with_parents[person]['father_gene'], people_with_parents[person]['mother_gene'])
            if person in have_trait:
                prob = prob*PROBS["trait"][0][True]
            else:
                prob = prob*PROBS["trait"][0][False]
    return prob


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        prob_0 = probabilities[person]["gene"][0]
        prob_1 = probabilities[person]["gene"][1]
        prob_2 = probabilities[person]["gene"][2]

        trait_t = probabilities[person]["trait"][True]
        trait_f = probabilities[person]["trait"][False]

        probabilities[person]["gene"][0] = prob_0/(prob_0+prob_1+prob_2)
        probabilities[person]["gene"][1] = prob_1/(prob_0+prob_1+prob_2)
        probabilities[person]["gene"][2] = prob_2/(prob_0+prob_1+prob_2)
        probabilities[person]["trait"][True] = trait_t/(trait_t+trait_f)
        probabilities[person]["trait"][False] = trait_f/(trait_t+trait_f)


def child_gene_probability(child_gene, father_gene, mother_gene):
    mutation_p = PROBS["mutation"]
    if child_gene == 0:
        if father_gene == 0:
            if mother_gene == 0:
                return (1 - mutation_p)*(1 - mutation_p) # both no mutation
            elif mother_gene == 1:
                # first one represents when mother passes the gene and the second one represents when mother doesn't pass the gene
                return 0.5*(1 - mutation_p)
            else:
                # no mutation for father gene 0 and mutation for mother gene 1
                return (1 - mutation_p)*(mutation_p)
        elif father_gene == 1:
            if mother_gene == 0:
                # first one:mutation for father and no mutation for mother when father passed the gene
                return 0.5*(1 - mutation_p)
            elif mother_gene == 1:
                # 0.25*mutation_p + 0.25*(1-mutation_p)
                return 0.25
            else:
                return 0.5*mutation_p
        else: # father has 2 genes
            if mother_gene == 0:
                return mutation_p*(1-mutation_p)
            elif mother_gene == 1:
                return 0.5*mutation_p
            else:
                return mutation_p*mutation_p
    elif child_gene == 1:
        if father_gene == 0:
            if mother_gene == 0:
                return mutation_p*(1-mutation_p) + (1-mutation_p)*mutation_p
            elif mother_gene == 1:
                return 0.5*((1-mutation_p)*(1-mutation_p)+mutation_p*mutation_p)+ 0.5*(mutation_p*(1-mutation_p)+(1-mutation_p)*mutation_p)
            else:
                return (1-mutation_p)*(1-mutation_p) + (mutation_p)*mutation_p
        elif father_gene == 1:
            if mother_gene == 0:
                return 0.5*((1-mutation_p)*(1-mutation_p)+mutation_p*mutation_p)+ 0.5*(mutation_p*(1-mutation_p)+(1-mutation_p)*mutation_p)
            elif mother_gene == 1:
                return 0.25*(mutation_p*(1-mutation_p)*2) + 0.25*((1-mutation_p)*(1-mutation_p)+mutation_p*mutation_p)*2 + 0.25*(mutation_p*(1-mutation_p) + (1-mutation_p)*mutation_p)
            else:
                return 0.5*child_gene_probability(1,1,1)+0.5*child_gene_probability(1,0,1)
        else:
            if mother_gene == 0:
                return child_gene_probability(1, 0, 2)
            elif mother_gene == 1:
                return child_gene_probability(1, 1, 2)
            else:
                return mutation_p*(1-mutation_p)*2
    else: # child 2 genes
        if father_gene == 0:
            if mother_gene == 0:
                return mutation_p*mutation_p
            elif mother_gene == 1:
                return 0.5*mutation_p
            else:
                return mutation_p*(1-mutation_p)
        elif father_gene == 1:
            if mother_gene == 0:
                return 0.5*mutation_p
            elif mother_gene == 1:
                return 0.25*(1-mutation_p)*(1-mutation_p)+0.25*(1-mutation_p)*mutation_p*2+0.25*mutation_p*mutation_p
            else:
                return 0.5*(1-mutation_p)
        else:
            if mother_gene == 0:
                return child_gene_probability(2, 0, 2)
            elif mother_gene == 1:
                return child_gene_probability(2, 1, 2)
            else:
                return (1-mutation_p)*(1-mutation_p)


def num_of_genes(person, one_gene, two_genes):
    if person in one_gene:
        return 1
    elif person in two_genes:
        return 2
    else:
        return 0


if __name__ == "__main__":
    main()
