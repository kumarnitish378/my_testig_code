#include <iostream>
#include <fstream>
#include <string>

using namespace std;

int main() {
    // Replace "your_text_file.txt" with the actual file path
    const string textFilePath = "phase_voltages.txt";

    // Open the text file
    ifstream file(textFilePath);

    // Check if the file is opened successfully
    if (!file.is_open()) {
        cerr << "Error opening file: " << textFilePath << endl;
        return 1;
    }

    // Read and display the content of the text file
    string line;
    while (getline(file, line)) {
        cout << line << endl;
    }



    // Close the file
    file.close();

    return 0;
}
