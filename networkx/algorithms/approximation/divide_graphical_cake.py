def two_agents_approx_cake(k: int) -> float:
    """
 finds the the best approximation for dividing a graphical cake when both of the agents gets overall of
 totatl of at most k + 1 connected pieces.
 Based on the article Dividing a Graphical Cake by Xiaohui Bei and Warut Suksompong from 2019.
 Link to the article - https://arxiv.org/pdf/1910.14129.pdf
 The algorithm is lemma 4.16 in the article.
 Programmer: Eran Katz
 Parameters
 ----------
 k - an integer.
 Represents the amount of connected pieces the agents will get overall, which is total of at most k + 1.

 Returns
 -------
 The approximation of the algo. It will be at most 1/2 - 1/(2*3^k). This number represents the amount of "cake" both
 agents will get.

 Example 1
 >>> two_agents_approx_cake(2)
 4/9
  >>> two_agents_approx_cake(1)
 1/3
  >>> two_agents_approx_cake(3)
 13/27
 """
    pass
