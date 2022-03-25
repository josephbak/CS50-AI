import os
import random
import re
import sys
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages
# done
def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    num_of_pages = len(corpus.keys())

    # if no link, i.e. num_links == 0, then just return equal probability.
    proba_dist_dict = {key: 1/num_of_pages for key in list(corpus.keys())}
    # if there is at least one link
    if num_links(corpus, page) != 0:
        linked_pages_set = corpus[page]
        for key in proba_dist_dict.keys():
            if key in linked_pages_set:
                proba_dist_dict[key] = damping_factor/len(linked_pages_set) + (1 - damping_factor)/num_of_pages
            else:
                proba_dist_dict[key] =(1 - damping_factor)/num_of_pages 
    return proba_dist_dict

# done
def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    proba_dist_dict = {key: 0 for key in list(corpus.keys())}
    for i in range(n):
        if i == 0:
            sample = random.choice(list(proba_dist_dict.keys()))
            proba_dist_dict[sample] += 1/n
        else:
            transition_prob_dict = transition_model(corpus, sample, damping_factor)
            sample = random.choices(list(transition_prob_dict.keys()), weights=transition_prob_dict.values(), k=1)[0]
            proba_dist_dict[sample] += 1/n
    return proba_dist_dict


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    all_pages = list(corpus.keys())
    num_of_pages = len(all_pages)

    # pages with no link to
    # page_without_link_to = set()
    # for page in all_pages:
    #     if num_links(corpus, page) == 0:
    #         page_without_link_to.add(page)

    # if page has no link, it has one link for every page in the corpus including itself.
    for page in all_pages:
        if num_links(corpus, page) == 0:
            corpus[page] = set(all_pages)
    # print(corpus)

    # reversed_corpus is the link-from dictionary
    reversed_corpus = reverse_corpus(corpus)
    # print(reversed_corpus)

    temp = {key: 1/num_of_pages for key in all_pages}
    proba_dist_dict = {key: 1/num_of_pages for key in all_pages}

    while True:
        for page in all_pages:
            # This part is for every page
            proba_dist_dict[page] = (1 - damping_factor)/num_of_pages
            # print(proba_dist_dict)
            # link from part
            for from_page in reversed_corpus[page]:
                # print(f"the page is {page}.")
                # print(f"the from pages are {from_page}")
                proba_dist_dict[page] += damping_factor * (temp[from_page]/len(corpus[from_page]))

        # print(f"probability dict: {proba_dist_dict}")
        # print(f"temp dict: {temp}")
        if max([abs(proba_dist_dict[key] - temp[key]) for key in all_pages]) <= 0.001:
            # print(counter)
            break
        else:
            temp = copy.deepcopy(proba_dist_dict)
            # print(temp)

    # print(sum(proba_dist_dict.values()))
    return proba_dist_dict

######my functions
def num_links(corpus, page):
    return len(corpus[page])

def reverse_corpus(corpus):
    all_pages = list(corpus.keys())

    # corpus is a link-to dictionary. This is a link-from dictionary.
    link_from_dict = {key: set() for key in all_pages}
    for key1 in all_pages:
        for key2 in all_pages:
            if key1 == key2:
                pass
            else:
                if key1 in corpus[key2]:
                    link_from_dict[key1].add(key2)

    return link_from_dict


if __name__ == "__main__":
    main()
