import numpy as np
import matplotlib.pyplot as plt
from skimage import io, color
from skimage.feature import hog
from skimage import exposure
from scipy.spatial import distance
import os
import itertools

def load_and_preprocess_image(image_path):
    """Loads and preprocesses an image.

    Args:
        image_path (str): Path to the image file.

    Returns:
        numpy.ndarray: Grayscale version of the image.
    """
    try:
        image = io.imread(image_path)
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None

    # Handle alpha channel if present
    if image.shape[2] == 4:
        image = image[:, :, :3]  # Extract RGB channels

    gray_image = color.rgb2gray(image)
    return gray_image

def compute_hog_features(image):
    """Computes HOG features for an image.

    Args:
        image (numpy.ndarray): Input image (grayscale).

    Returns:
        tuple: A tuple containing the HOG features and the rescaled HOG image.
    """
    hog_features, hog_image = hog(image, visualize=True)
    hog_image_rescaled = exposure.rescale_intensity(hog_image, in_range=(0, 10))
    return hog_features, hog_image_rescaled

def calculate_similarity(hog_features1, hog_features2):
    """Calculates the Euclidean distance between two HOG feature vectors.

    Args:
        hog_features1 (numpy.ndarray): First HOG feature vector.
        hog_features2 (numpy.ndarray): Second HOG feature vector.

    Returns:
        float: Euclidean distance between the two feature vectors.
    """
    return distance.euclidean(hog_features1, hog_features2)

def find_most_similar_images(image_dir):
    """Finds the pair of images with the most similar HOG features in a directory.

    Args:
        image_dir (str): Path to the directory containing the images.

    Returns:
        tuple: A tuple containing information about the most similar image pair.
               This includes the minimum similarity score, the indices of the images, 
               and preprocessed image data (original, HOG features, HOG image) for visualization.
               Returns None if no images are found or an error occurs.
    """
    image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
    
    if not image_paths:
        print(f"No images found in directory: {image_dir}")
        return None

    hog_data = []
    for path in image_paths:
        image = load_and_preprocess_image(path)
        if image is None: # Handle potential loading errors
            continue
        hog_features, hog_image = compute_hog_features(image)
        hog_data.append([image, hog_features, hog_image, path])

    num_images = len(hog_data)
    if num_images < 2:
        print("Not enough images to compare similarity.")
        return None

    min_similarity = float('inf')
    most_similar_pair = None

    for i, j in itertools.combinations(range(num_images), 2): # Efficiently iterate through all image pairs
        similarity = calculate_similarity(hog_data[i][1], hog_data[j][1])
        if similarity < min_similarity:
            min_similarity = similarity
            most_similar_pair = (i, j)


    return min_similarity, most_similar_pair, hog_data


def visualize_results(min_similarity, most_similar_pair, hog_data):
    """Visualizes the most similar image pair and their HOG features."""

    if most_similar_pair is None or hog_data is None:
        print("No similar images to visualize.")
        return

    i, j = most_similar_pair
    image1, hog_features1, hog_image1, path1 = hog_data[i]
    image2, hog_features2, hog_image2, path2 = hog_data[j]

    print(f'Similarity (Euclidean Distance): {min_similarity} between {path1} and {path2}')

    fig, ax = plt.subplots(2, 3, figsize=(12, 8))

    ax[0, 0].imshow(image1, cmap='gray')
    ax[0, 0].axis('off')
    ax[0, 0].set_title('Image 1')

    ax[0, 1].imshow(hog_image1, cmap='hot')
    ax[0, 1].axis('off')
    ax[0, 1].set_title('HOG Features Image 1')

    ax[0, 2].hist(hog_features1, bins=50, color='gray')
    ax[0, 2].set_title('HOG Features Histogram Image 1')


    ax[1, 0].imshow(image2, cmap='gray')
    ax[1, 0].axis('off')
    ax[1, 0].set_title('Image 2')


    ax[1, 1].imshow(hog_image2, cmap='hot')
    ax[1, 1].axis('off')
    ax[1, 1].set_title('HOG Features Image 2')


    ax[1, 2].hist(hog_features2, bins=50, color='gray')
    ax[1, 2].set_title('HOG Features Histogram Image 2')

    plt.tight_layout()
    plt.show()



def main(image_dir):
    """Main function to find and visualize the most similar images."""
    results = find_most_similar_images(image_dir)
    if results:
        min_similarity, most_similar_pair, hog_data = results
        visualize_results(min_similarity, most_similar_pair, hog_data)

if __name__ == "__main__":
    image_dir = 'cropped_images'
    main(image_dir)