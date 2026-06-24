import os
import sys
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
        dataset_name: The name of the dataset (e.g. BRATS, TCIA, ImageNet, CBIS-DDSM, MNIST, CIFAR-10).
    """
    datasets = {
        "brats": "Dataset: Brain Tumor Segmentation (BraTS). Size: ~2,000 patient scans (multimodal MRI: T1, T1c, T2, FLAIR). Access: Public, but requires registering on Synapse platform. Difficulty: Advanced (3D spatial registration, voxel segmentation).",
        "tcia": "Dataset: The Cancer Imaging Archive (TCIA). Size: Terabytes of medical scans. Access: Public. Difficulty: Intermediate to Advanced.",
        "imagenet": "Dataset: ImageNet Large Scale Visual Recognition Challenge (ILSVRC). Size: 1.2 million images across 1,000 classes. Access: Public. Difficulty: Hard (due to computational size).",
        "cbis-ddsm": "Dataset: Curated Breast Imaging Subset of DDSM. Size: ~1,500 mammography cases. Access: Public (TCIA). Difficulty: Intermediate (mammogram cropping, ROI annotations).",
        "mnist": "Dataset: MNIST Handwritten Digits. Size: 70,000 28x28 grayscale images. Access: Public (built-in). Difficulty: Very Easy.",
        "cifar-10": "Dataset: CIFAR-10. Size: 60,000 32x32 color images. Access: Public. Difficulty: Easy."
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

if __name__ == "__main__":
    mcp.run("stdio")
