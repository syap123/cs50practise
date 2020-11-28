import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000
iteration_consistency_requirement = 0.001


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


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.

    """

    links = corpus[page]
    num_links = len(links)
    num_pages = len(corpus)

    output = {}
    for current_page in corpus:
        if current_page in links:
            output[current_page] = ((damping_factor) / (num_links)) + ((1 - damping_factor)/ num_pages)
        else:
            output[current_page] = ((1 - damping_factor)/ num_pages)
    return output

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_counter = {}
    # populate page counter. 
    for key in corpus.keys():
        page_counter[key] = 0

    current_page = random.choices(population = list(corpus.keys()))[0]
    page_counter[current_page] = page_counter[current_page] + 1
    # start iterating from 2 since we already added the first page into page_counter
    i = 2 
    while i <= n:
        i = i + 1
        next_distribution = transition_model(corpus,current_page,damping_factor)
        pages = list(next_distribution.keys())
        probabilities = list(next_distribution.values())
        current_page = random.choices(population = pages, weights = probabilities)[0]
        page_counter[current_page] = page_counter[current_page] + 1

    for page_count in page_counter:
        page_counter[page_count] = page_counter[page_count]/n

    return page_counter


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank_tracker = {}
    num_pages_in_corpus = len(corpus)
    for key in corpus.keys():
        pagerank_tracker[key] = 1/num_pages_in_corpus

    
    while True:
        pagerank_difference_max = 0
        for page_p in pagerank_tracker:
            prev_pagerank = pagerank_tracker[page_p]
            sum_pri_over_numlinks = 0
            for page_i in corpus:
                if (page_p in corpus[page_i]):
                    sum_pri_over_numlinks = sum_pri_over_numlinks + pagerank_tracker[page_i]/len(corpus[page_i])
                elif (len(corpus[page_i]) == 0):
                    sum_pri_over_numlinks = sum_pri_over_numlinks + pagerank_tracker[page_i]/num_pages_in_corpus                    
            new_pagerank = ((1-damping_factor) / num_pages_in_corpus) + (damping_factor * sum_pri_over_numlinks)
            # check pagerank difference
            pagerank_difference_max = max(abs(new_pagerank - prev_pagerank),pagerank_difference_max)
            # update new pagerank in tracker
            pagerank_tracker[page_p] = new_pagerank
        if pagerank_difference_max <= iteration_consistency_requirement:
            break

    return pagerank_tracker





if __name__ == "__main__":
    main()
