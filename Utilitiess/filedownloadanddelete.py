import requests
import os

def download_file(url, filename):
    """
    Download a file from a URL and save it locally in the 'data' folder as a .pdf file.

    Parameters:
    - url (str): The URL of the file to download.
    - filename (str): The local filename to save the file as. Will be saved as a .pdf file.
    """
    try:
        # Ensure the 'data' directory exists
        os.makedirs('data', exist_ok=True)

        # Append '.pdf' extension if not already present in the filename
        if not filename.endswith('.pdf'):
            filename += '.pdf'

        # Full path to save the file
        filepath = os.path.join('data', filename)

        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for HTTP errors

        # Open a local file with write-binary mode
        with open(filepath, 'wb') as file:
            # Write the response content in chunks
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        print(f'Download completed successfully. File saved as "{filepath}".')
    except requests.exceptions.HTTPError as errh:
        print(f'HTTP Error: {errh}')
    except requests.exceptions.ConnectionError as errc:
        print(f'Connection Error: {errc}')
    except requests.exceptions.Timeout as errt:
        print(f'Timeout Error: {errt}')
    except requests.exceptions.RequestException as err:
        print(f'Error: {err}')

def delete_file(filename):
    """
    Delete a file from the 'data' directory.

    Parameters:
    - filename (str): The filename of the file to delete.
    """
    try:
        # Full path of the file
        filepath = os.path.join('data', filename)
        os.remove(filepath)
        print(f'File "{filepath}" has been deleted successfully.')
    except FileNotFoundError:
        print(f'File "{filepath}" does not exist.')
    except Exception as e:
        print(f'An error occurred while deleting the file: {e}')


# Call the function to download and save as a .pdf file
download_file("https://files.eric.ed.gov/fulltext/EJ1172284.pdf", "nehal")
