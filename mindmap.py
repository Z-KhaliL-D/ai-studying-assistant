import os
import requests
from dotenv import load_dotenv
import graphviz

API_URL = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization":"Bearer YOUR_API_KEY"} 

def get_mindmap(text, parse_description=""):
    promptM = f"""
    ### Instructions:
    1. **Extract Key Information**: Identify the main themes, subtopics, and supporting details from the provided text.
    2. **Hierarchical Structure**: Organize the information into a clear hierarchy, with main branches representing primary topics and sub-branches for related ideas.
    3. **Conciseness**: Use short, descriptive phrases or keywords to represent each node in the mind map.
    4. **Logical Connections**: Ensure all connections between nodes are meaningful and reflect the relationships in the content.
    5. **Visual Appeal**: Suggest a clean and professional design for the mind map, with appropriate use of colors, icons, and spacing to enhance readability.
    Create a hierarchical markdown mindmap from the following text. 
    Use proper markdown heading syntax (# for main topics, ## for subtopics, ### for details).
    Focus on the main concepts and their relationships.
    Include relevant details and connections between ideas.
    Keep the structure clean and organized.
    
    Format the output exactly like this example:
    # Main Topic
    ## Subtopic 1
    ### Detail 1
    - Key point 1
    - Key point 2
    ### Detail 2
    ## Subtopic 2
    ### Detail 3
    ### Detail 4
    Example:
    # Artificial Intelligence
    ## Machine Learning
    ### Supervised Learning
    - Uses labeled data
    - Common algorithms: Linear Regression, Decision Trees
    ### Unsupervised Learning
    - Finds patterns in unlabeled data
    - Common algorithms: K-Means, PCA
    ## Deep Learning
    ### Neural Networks
    - Inspired by the human brain
    - Layers: Input, Hidden, Output
    ### Applications
    - Image recognition
    - Natural Language Processing
    
    Important: 
    Text to analyze: {text}
    Respond only with the markdown mindmap, no additional text.
    
    ### Information to Extract:
    {parse_description}

    ### Output:
    Respond only with the markdown mind map, no additional text, comments, or any other extras.
    """
    payload = {
        "model": "llama-3.3-70b-versatile", 
        "messages": [
            {"role": "user", "content": promptM}
        ],
        "temperature": 0.1,
        "max_tokens": 1000,
        "top_p": 0.1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }

    try:
        print("Sending API request...")
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()  # Raises an error for bad responses
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:

            return result["choices"][0]["message"]["content"]  # Extract the mind map content
        else:
            print("Unexpected API response format:", result)
            return None
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}, Response Text: {response.text if 'response' in locals() else 'No response'}")
        return None
import urllib.parse

def convert_markdown_to_graphviz(markdown_text):
    dot = graphviz.Digraph(format='png')
    dot.attr(dpi='300')
    
    current_nodes = {'#': '', '##': '', '###': ''}

    for line in markdown_text.split('\n'):
        if line.startswith('# '):
            node = line.replace('# ', '').strip()
            current_nodes['#'] = node
            dot.node(node, node, shape='box', style='filled', fillcolor='lightblue')
        elif line.startswith('## '):
            node = line.replace('## ', '').strip()
            current_nodes['##'] = node
            dot.node(node, node, shape='ellipse', style='filled', fillcolor='lightgrey')
            dot.edge(current_nodes['#'], node)
        elif line.startswith('### '):
            node = line.replace('### ', '').strip()
            current_nodes['###'] = node
            dot.node(node, node, shape='ellipse')
            dot.edge(current_nodes['##'], node)
        elif line.startswith('- '):
            point = line.replace('- ', '').strip()
            dot.node(point, point, shape='plaintext')
            dot.edge(current_nodes['###'], point)

    return dot


def render_img(mindmap_result):
    try:
        graph = convert_markdown_to_graphviz(mindmap_result)
        image_path = graph.render(filename='mindmap', cleanup=True)
        return image_path  
    except Exception as e:
        print(f"Error rendering image: {e}")
        return None
