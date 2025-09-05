# Graphical Cake Division — חלוקה הוגנת של גרף

This Flask web app demonstrates a fair division algorithm for graphs, based on the paper:

"Fair and Efficient Cake Division with Connected Pieces"  
Xiaohui Bei and Warut Suksompong, 2019  
[https://arxiv.org/abs/1910.14129](https://arxiv.org/pdf/1910.14129#subsection.4.1)

---

## Project Overview

The system allows:

- Inputting a graph manually or generating a random connected graph  
- Defining vertex valuations for two agents  
- Producing a fair division of edges based on contiguous oriented labeling and knife simulation  

The goal is to split the edges of the graph into two connected parts such that each agent receives roughly half of the total value, calculated from vertex valuations.

---

## Algorithm Summary

1. **Contiguous Oriented Labeling** (in `contiguous_labeling.py`):  
   Labels edges continuously using ear decomposition, producing an ordered list of oriented edges.

2. **Fair Division (in `app.py`):**  
   Uses vertex valuations to simulate a knife moving over edges in order, assigning edges to agents based on cumulative vertex values of edges.

---

## Main Features

- Manual edge and valuation input  
- Random connected graph generation (default 5 nodes, probability 0.5)  
- Vertex valuations input for two agents  
- Graph visualization via vis-network  
- Direct output display on the same page  
- Hebrew interface support  

---

## Installation and Running

1. Install dependencies:
   
   pip install -r requirements.txt
   
2. Run the Flask app:

python app.py

3. Open your browser to:

   https://ghia48.serhan.csariel.xyz/



  ## Project Structure
  project/
│
├── app.py                  # אפליקציית Flask הראשית
├── contiguous_labeling.p   # האלגוריתם לתיוג רציף 
├── templates/
│   ├── index.html          # דף ראשי עם טופס וקלט
│   └── about.html          # דף מידע נוסף 
├── requirements.txt
└── README.md


    

