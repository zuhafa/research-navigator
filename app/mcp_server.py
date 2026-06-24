import os
import sys
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ResearchNavigatorKnowledgeBase")

@mcp.tool()
def check_prerequisites(topic: str) -> str:
    """Gets the required learning roadmap for a research topic or library.

    Args:
        topic: The library or research concept (e.g. Transformers, CNNs, GNNs, Diffusion Models, PyTorch).
    """
    roadmaps = {
        "transformers": "Roadmap: 1. Python, 2. PyTorch, 3. Neural Networks, 4. Attention Mechanisms, 5. Transformer Architecture (Self-Attention, Multi-head attention). Recommended Prep Time: 4 weeks.",
        "cnns": "Roadmap: 1. Python, 2. NumPy, 3. Linear Algebra, 4. Convolutional Layer operations, 5. Pooling, 6. ResNet/VGG architectures. Recommended Prep Time: 3 weeks.",
        "gnns": "Roadmap: 1. Graph Theory basics, 2. PyTorch Geometric, 3. Message Passing Neural Networks. Recommended Prep Time: 5 weeks.",
        "diffusion models": "Roadmap: 1. Calculus & Probability, 2. U-Net Architecture, 3. Forward & Reverse Markov chains. Recommended Prep Time: 6 weeks.",
        "pytorch": "Roadmap: 1. Python OOP, 2. Tensors, 3. Autograd, 4. Dataset & DataLoader. Recommended Prep Time: 1 week."
    }
    key = topic.lower().strip()
    return roadmaps.get(key, f"Roadmap for {topic}: 1. Basic Python, 2. Neural Networks, 3. Specific model architecture. Recommended Prep: 3-4 weeks.")

@mcp.tool()
def check_dataset_spec(dataset_name: str) -> str:
    """Queries details, size, and public availability of a research dataset.

    Args:
        dataset_name: The name of the dataset (e.g. BRATS, TCIA, ImageNet, CBIS-DDSM, MNIST, CIFAR-10, Breast MRI Dataset, BUSI, HAM10000, PlantVillage, EuroSAT, Sentinel-2, Rice Leaf Disease).
    """
    datasets = {
        "brats": "Dataset: Brain Tumor Segmentation (BraTS). Size: ~2,000 patient scans (multimodal MRI: T1, T1c, T2, FLAIR). Access: Public, but requires registering on Synapse platform. Difficulty: Advanced (3D spatial registration, voxel segmentation).",
        "tcia": "Dataset: The Cancer Imaging Archive (TCIA). Size: Terabytes of medical scans. Access: Public. Difficulty: Intermediate to Advanced.",
        "imagenet": "Dataset: ImageNet Large Scale Visual Recognition Challenge (ILSVRC). Size: 1.2 million images across 1,000 classes. Access: Public. Difficulty: Hard (due to computational size).",
        "cbis-ddsm": "Dataset: Curated Breast Imaging Subset of DDSM. Size: ~1,500 mammography cases. Access: Public (TCIA). Difficulty: Intermediate (mammogram cropping, ROI annotations).",
        "mnist": "Dataset: MNIST Handwritten Digits. Size: 70,000 28x28 grayscale images. Access: Public (built-in). Difficulty: Very Easy.",
        "cifar-10": "Dataset: CIFAR-10. Size: 60,000 32x32 color images. Access: Public. Difficulty: Easy.",
        "breast mri dataset": "Dataset: Breast MRI Dataset. Size: ~1,000 cases of dynamic contrast-enhanced (DCE) breast MRI scans. Access: Public (TCIA). Difficulty: Advanced (3D image segmentation, motion correction).",
        "busi": "Dataset: Breast Ultrasound Image (BUSI) Dataset. Size: 780 ultrasound images of breast cancer (normal, benign, malignant). Access: Public (Kaggle). Difficulty: Intermediate (lesion classification, contour segmentation).",
        "ham10000": "Dataset: HAM10000 (Human Against Machine). Size: 10,015 dermatoscopic images of skin lesions across 7 diagnostic categories. Access: Public (Harvard Dataverse / Kaggle). Difficulty: Intermediate (imbalanced classes, skin color variations).",
        "plantvillage": "Dataset: PlantVillage. Size: 54,306 images of healthy and diseased crop leaves across 38 class labels. Access: Public (Kaggle). Difficulty: Easy to Intermediate (fine-grained multiclass classification).",
        "eurosat": "Dataset: EuroSAT. Size: 27,000 labeled patches representing 10 land cover classes. Access: Public (GitHub/TensorFlow Datasets). Difficulty: Easy (multiclass Sentinel-2 satellite image classification).",
        "sentinel-2": "Dataset: Sentinel-2 Multispectral Data. Size: Global coverage. Access: Public (Copernicus Browser). Difficulty: Advanced (handling 13 multispectral bands, temporal sequence processing).",
        "rice leaf disease": "Dataset: Rice Leaf Disease Dataset. Size: ~120 images showing Bacterial blight, Brown spot, and Leaf smut. Access: Public (Kaggle). Difficulty: Easy (classification with small dataset size, requires augmentation)."
    }
    key = dataset_name.lower().strip()
    for k in datasets:
        if k in key:
            return datasets[k]
    return f"Dataset: {dataset_name}. Access: Check Kaggle or official academic homepage. Difficulty: General preprocessing required."

@mcp.tool()
def estimate_complexity(model_type: str) -> str:
    """Evaluates library dependencies and typical implementation time for common AI models.

    Args:
        model_type: The name of the model type or architecture (e.g. U-Net, ResNet, ViT, GPT-2).
    """
    complexities = {
        "u-net": "Architecture: U-Net (Encoder-Decoder with skip connections). Primary Libraries: PyTorch / TensorFlow, Albumentations (image augmentations). Build Difficulty: Intermediate. Typical Implementation: 2 weeks.",
        "resnet": "Architecture: Residual Network. Primary Libraries: torchvision / keras. Build Difficulty: Easy (using pretrained), Intermediate (building from scratch). Typical Implementation: 1 week.",
        "vit": "Architecture: Vision Transformer. Primary Libraries: PyTorch, timm (PyTorch Image Models). Build Difficulty: Advanced (requires large dataset and compute). Typical Implementation: 3 weeks.",
        "gpt-2": "Architecture: Autoregressive Decoder Transformer. Primary Libraries: HuggingFace Transformers, PyTorch. Build Difficulty: Advanced. Typical Implementation: 4 weeks."
    }
    key = model_type.lower().strip()
    for k in complexities:
        if k in key:
            return complexities[k]
    return f"Complexity: Intermediate. Recommended Libraries: PyTorch/TensorFlow. Build Difficulty: General model implementation. Typical build time: 2-3 weeks."

@mcp.tool()
def get_learning_path(topic: str) -> Dict[str, Any]:
    """Generates a structured weekly learning roadmap for a research topic or library.

    Args:
        topic: The library or research concept (e.g. Transformers, CNNs, GNNs, Diffusion Models, PyTorch).
    """
    paths = {
        "transformers": {
            "topic": "Transformers",
            "weeks": 4,
            "week_1": ["Python", "NumPy", "Linear Algebra"],
            "week_2": ["PyTorch Basics", "Tensors", "Autograd"],
            "week_3": ["Neural Networks", "Backpropagation", "Sequence Models"],
            "week_4": ["Attention Mechanisms", "Transformers", "Self-Attention"]
        },
        "cnns": {
            "topic": "CNNs",
            "weeks": 3,
            "week_1": ["Python", "NumPy", "Matrix Calculus"],
            "week_2": ["PyTorch Tensors", "Convolutional Layers", "Pooling"],
            "week_3": ["ResNet Architecture", "Transfer Learning", "Image Classification"]
        },
        "gnns": {
            "topic": "GNNs",
            "weeks": 5,
            "week_1": ["Python", "NetworkX", "Graph Theory Basics"],
            "week_2": ["PyTorch Geometric Basics", "Node Embeddings"],
            "week_3": ["Graph Convolutional Networks (GCN)", "Message Passing"],
            "week_4": ["Graph Attention Networks (GAT)", "Pooling Layers"],
            "week_5": ["Link Prediction", "Graph Classification Projects"]
        },
        "diffusion models": {
            "topic": "Diffusion Models",
            "weeks": 6,
            "week_1": ["Probability Theory", "Calculus", "SDEs"],
            "week_2": ["U-Net Architecture", "Skip Connections"],
            "week_3": ["Forward Diffusion Process", "Markov Chains"],
            "week_4": ["Reverse Denoising Process", "Score Matching"],
            "week_5": ["Classifier-Free Guidance", "Latent Diffusion"],
            "week_6": ["Stable Diffusion Implementation", "Text-to-Image Generation"]
        },
        "pytorch": {
            "topic": "PyTorch",
            "weeks": 2,
            "week_1": ["Python OOP", "Tensors Operations", "Autograd"],
            "week_2": ["nn.Module", "Dataset & DataLoader", "Optimization Loops"]
        }
    }
    
    key = topic.lower().strip()
    for k in paths:
        if k in key:
            return paths[k]
            
    # Default fallback
    return {
        "topic": topic,
        "weeks": 4,
        "week_1": ["Basic Python", "NumPy", "Data Preprocessing"],
        "week_2": ["Neural Network Foundations", "Loss Functions", "Optimizers"],
        "week_3": [f"{topic} Architecture Concepts", "Forward Pass Implementation"],
        "week_4": [f"Training {topic} Model", "Evaluation Metrics", "Fine-Tuning"]
    }

@mcp.tool()
def get_project_templates(topic: str) -> Dict[str, str]:
    """Retrieves beginner, intermediate, and advanced project templates for a given topic.

    Args:
        topic: The library or research concept (e.g. Transformers, CNNs, GNNs, Diffusion Models, PyTorch).
    """
    templates = {
        "transformers": {
            "beginner": "Text Classification with IMDB reviews using DistilBERT",
            "intermediate": "Sequence-to-Sequence Translator (English to Spanish) from scratch",
            "advanced": "GPT-2 Style Decoder-Only Transformer Language Model from scratch"
        },
        "cnns": {
            "beginner": "MNIST Digit Classifier using simple CNN layers",
            "intermediate": "Medical Image Classifier (Pneumonia Detection in Chest X-rays)",
            "advanced": "Custom ResNet Implementation for Fine-grained Species Classification"
        },
        "gnns": {
            "beginner": "Cora Citation Network Node Classification using GCNs",
            "intermediate": "Molecular Property Prediction (ESOL dataset) using PyTorch Geometric",
            "advanced": "Fraud Detection on Financial Transaction Graphs with GraphSAGE"
        },
        "diffusion models": {
            "beginner": "1D Noise Denoising Toy Example",
            "intermediate": "DDPM (Denoising Diffusion Probabilistic Model) on MNIST Digits",
            "advanced": "Latent Diffusion Model for Super-Resolution on Custom Datasets"
        },
        "pytorch": {
            "beginner": "Fully Connected Feedforward Neural Network on Iris Dataset",
            "intermediate": "Image Augmentation Pipeline and Custom Dataset Loader",
            "advanced": "Custom CUDA Extension for Accelerated Activation Function"
        }
    }
    
    key = topic.lower().strip()
    for k in templates:
        if k in key:
            return templates[k]
            
    # Default fallback
    return {
        "beginner": f"Basic {topic} Classification Task",
        "intermediate": f"Custom {topic} Model with Preprocessing Pipeline",
        "advanced": f"State-of-the-Art {topic} Research Paper Replication"
    }

@mcp.tool()
def get_research_domain(topic: str) -> Dict[str, str]:
    """Categorizes a research topic into its scientific domain, subfield, and real-world impact.

    Args:
        topic: The library or research concept (e.g. Transformers, CNNs, GNNs, Diffusion Models, PyTorch, Medical Imaging).
    """
    domains = {
        "transformers": {
            "domain": "Natural Language Processing / Computer Vision",
            "subfield": "Large Language Models & Vision Transformers",
            "difficulty": "Advanced",
            "industry_relevance": "Critical",
            "real_world_impact": "Powers modern search engines, translation tools, and generative AI systems."
        },
        "cnns": {
            "domain": "Computer Vision",
            "subfield": "Image Classification & Object Detection",
            "difficulty": "Intermediate",
            "industry_relevance": "High",
            "real_world_impact": "Enables automated medical diagnosis, autonomous vehicle navigation, and surveillance systems."
        },
        "gnns": {
            "domain": "Geometric Deep Learning",
            "subfield": "Graph Representation & Relational Reasoning",
            "difficulty": "Advanced",
            "industry_relevance": "High",
            "real_world_impact": "Accelerates drug discovery, protein folding analysis, and social network recommendation systems."
        },
        "diffusion models": {
            "domain": "Generative Modeling",
            "subfield": "Probabilistic Denoising Generative Systems",
            "difficulty": "Advanced",
            "industry_relevance": "Very High",
            "real_world_impact": "Enables high-fidelity image synthesis, scientific data augmentation, and creative design tools."
        },
        "pytorch": {
            "domain": "Deep Learning Frameworks",
            "subfield": "Machine Learning Infrastructure",
            "difficulty": "Intermediate",
            "industry_relevance": "Universal",
            "real_world_impact": "De facto standard for academic AI research and industrial prototyping."
        },
        "medical imaging": {
            "domain": "Digital Health / Computer Vision",
            "subfield": "Diagnostic Radiology & Pathology Segmentation",
            "difficulty": "Advanced",
            "industry_relevance": "High",
            "real_world_impact": "Assists radiologists in early cancer detection and organ segmentation."
        }
    }
    
    key = topic.lower().strip()
    for k in domains:
        if k in key:
            return domains[k]
            
    # Default fallback
    return {
        "domain": "General Artificial Intelligence",
        "subfield": f"Applied {topic} Systems",
        "difficulty": "Intermediate",
        "industry_relevance": "Medium to High",
        "real_world_impact": f"Improves pipeline automation and decision-making for {topic} processes."
    }

@mcp.tool()
def get_readiness_rules(topic: str) -> Dict[str, int]:
    """Retrieves readiness evaluation weighting scores (percentages) for skills needed for a topic.

    Args:
        topic: The library or research concept (e.g. Transformers, CNNs, GNNs, Diffusion Models, PyTorch).
    """
    rules = {
        "transformers": {
            "python": 20,
            "machine_learning": 25,
            "deep_learning": 25,
            "projects": 20,
            "deployment": 10
        },
        "cnns": {
            "python": 25,
            "machine_learning": 30,
            "deep_learning": 20,
            "projects": 15,
            "deployment": 10
        },
        "gnns": {
            "python": 15,
            "machine_learning": 25,
            "deep_learning": 30,
            "projects": 20,
            "deployment": 10
        },
        "diffusion models": {
            "python": 15,
            "machine_learning": 20,
            "deep_learning": 35,
            "projects": 20,
            "deployment": 10
        },
        "pytorch": {
            "python": 35,
            "machine_learning": 30,
            "deep_learning": 15,
            "projects": 15,
            "deployment": 5
        }
    }
    
    key = topic.lower().strip()
    for k in rules:
        if k in key:
            return rules[k]
            
    # Default fallback
    return {
        "python": 20,
        "machine_learning": 25,
        "deep_learning": 25,
        "projects": 20,
        "deployment": 10
    }

if __name__ == "__main__":
    mcp.run("stdio")
