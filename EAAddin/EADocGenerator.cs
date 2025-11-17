using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using EA;

namespace EADocGenerator
{
    /// <summary>
    /// EA Addin for generating documentation using the Python generator
    /// Implements EA.Addin interface to integrate with Enterprise Architect
    /// </summary>
    [ComVisible(true)]
    [ClassInterface(ClassInterfaceType.AutoDual)]
    [Guid("8A6C6AC1-8B5E-4F5D-9E3C-2A4B5C6D7E8F")]
    [ProgId("EADocGenerator.EADocGeneratorAddin")]
    public class EADocGeneratorAddin
    {
        // EA Repository reference
        private Repository repository;

        // Menu constants
        private const string MENU_NAME = "-&EA Doc Generator";
        private const string MENU_GENERATE_ALL = "&Generate All Documentation";
        private const string MENU_GENERATE_USE_CASES = "Generate &Use Cases";
        private const string MENU_GENERATE_CLASSES = "Generate &Classes";
        private const string MENU_GENERATE_COMPONENTS = "Generate C&omponents";
        private const string MENU_GENERATE_STATE_MACHINES = "Generate &State Machines";
        private const string MENU_GENERATE_REQUIREMENTS = "Generate &Requirements";
        private const string MENU_EXTRACT_DIAGRAMS = "Extract &Diagrams (Windows Only)";
        private const string MENU_OPEN_OUTPUT = "&Open Output Folder";
        private const string MENU_SETTINGS = "&Settings";
        private const string MENU_ABOUT = "&About";

        /// <summary>
        /// Public constructor required for COM
        /// </summary>
        public EADocGeneratorAddin()
        {
            // TEMPORARY: Diagnostic message to verify EA loads the addin
            MessageBox.Show("EADocGeneratorAddin constructor called!", "EA Doc Generator - Debug", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        /// <summary>
        /// Called when EA starts - initialize the addin
        /// </summary>
        public string EA_Connect(Repository repository)
        {
            // TEMPORARY: Diagnostic message to verify EA calls EA_Connect
            MessageBox.Show("EA_Connect called!", "EA Doc Generator - Debug", MessageBoxButtons.OK, MessageBoxIcon.Information);
            this.repository = repository;
            return "EA Doc Generator";
        }

        /// <summary>
        /// Called when EA closes - cleanup
        /// </summary>
        public void EA_Disconnect()
        {
            GC.Collect();
            GC.WaitForPendingFinalizers();
        }

        /// <summary>
        /// Define the menu structure
        /// </summary>
        public object EA_GetMenuItems(Repository repository, string location, string menuName)
        {
            switch (menuName)
            {
                case "":
                    return MENU_NAME;
                case MENU_NAME:
                    string[] items = {
                        MENU_GENERATE_ALL,
                        MENU_GENERATE_USE_CASES,
                        MENU_GENERATE_CLASSES,
                        MENU_GENERATE_COMPONENTS,
                        MENU_GENERATE_STATE_MACHINES,
                        MENU_GENERATE_REQUIREMENTS,
                        "-",
                        MENU_EXTRACT_DIAGRAMS,
                        MENU_OPEN_OUTPUT,
                        "-",
                        MENU_SETTINGS,
                        MENU_ABOUT
                    };
                    return items;
            }
            return "";
        }

        /// <summary>
        /// Handle menu item clicks
        /// </summary>
        public void EA_MenuClick(Repository repository, string location, string menuName, string itemName)
        {
            switch (itemName)
            {
                case MENU_GENERATE_ALL:
                    GenerateDocumentation("all");
                    break;
                case MENU_GENERATE_USE_CASES:
                    GenerateDocumentation("use-cases");
                    break;
                case MENU_GENERATE_CLASSES:
                    GenerateDocumentation("classes");
                    break;
                case MENU_GENERATE_COMPONENTS:
                    GenerateDocumentation("components");
                    break;
                case MENU_GENERATE_STATE_MACHINES:
                    GenerateDocumentation("state-machines");
                    break;
                case MENU_GENERATE_REQUIREMENTS:
                    GenerateDocumentation("requirements");
                    break;
                case MENU_EXTRACT_DIAGRAMS:
                    ExtractDiagrams();
                    break;
                case MENU_OPEN_OUTPUT:
                    OpenOutputFolder();
                    break;
                case MENU_SETTINGS:
                    ShowSettings();
                    break;
                case MENU_ABOUT:
                    ShowAbout();
                    break;
            }
        }

        /// <summary>
        /// Get the path to the Python script directory
        /// Assumes the addin DLL is in EATools/EAAddin/bin/ folder
        /// </summary>
        private string GetScriptDirectory()
        {
            string addinPath = System.Reflection.Assembly.GetExecutingAssembly().Location;
            string eaToolsPath = Path.GetFullPath(Path.Combine(Path.GetDirectoryName(addinPath), "..", ".."));
            return eaToolsPath;
        }

        /// <summary>
        /// Generate documentation using Python script
        /// </summary>
        private void GenerateDocumentation(string docType)
        {
            try
            {
                // Save the repository first
                repository.SaveAllDiagrams();

                // Get repository path
                string repoPath = repository.ConnectionString;
                if (string.IsNullOrEmpty(repoPath))
                {
                    MessageBox.Show("Unable to determine repository path. Please save your model first.",
                        "EA Doc Generator", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }

                // Clean up the connection string to get file path
                if (repoPath.Contains("DBType="))
                {
                    // Parse EA connection string format
                    foreach (string part in repoPath.Split(';'))
                    {
                        if (part.Trim().StartsWith("Connect="))
                        {
                            repoPath = part.Substring(8).Trim();
                            break;
                        }
                    }
                }

                // Get paths
                string scriptDir = GetScriptDirectory();
                string pythonScript = Path.Combine(scriptDir, "sparx_doc_generator.py");
                string outputDir = Path.Combine(scriptDir, "docs");

                if (!System.IO.File.Exists(pythonScript))
                {
                    MessageBox.Show($"Python script not found at: {pythonScript}\n\nPlease ensure the addin is installed correctly.",
                        "EA Doc Generator", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return;
                }

                // Build command line arguments
                string args = $"\"{pythonScript}\" \"{repoPath}\" --output \"{outputDir}\"";

                if (docType != "all")
                {
                    args += $" --types {docType}";
                }

                // Show progress message
                repository.WriteOutput("System", $"EA Doc Generator: Starting documentation generation ({docType})...", 0);

                // Execute Python script
                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = args,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    WorkingDirectory = scriptDir
                };

                using (Process process = Process.Start(startInfo))
                {
                    // Show progress window
                    string output = process.StandardOutput.ReadToEnd();
                    string error = process.StandardError.ReadToEnd();
                    process.WaitForExit();

                    if (process.ExitCode == 0)
                    {
                        repository.WriteOutput("System", "EA Doc Generator: Documentation generated successfully!", 0);
                        repository.WriteOutput("System", output, 0);

                        DialogResult result = MessageBox.Show(
                            $"Documentation generated successfully!\n\nOutput location: {outputDir}\n\nWould you like to open the output folder?",
                            "EA Doc Generator",
                            MessageBoxButtons.YesNo,
                            MessageBoxIcon.Information);

                        if (result == DialogResult.Yes)
                        {
                            OpenOutputFolder();
                        }
                    }
                    else
                    {
                        repository.WriteOutput("System", "EA Doc Generator: Error generating documentation", 0);
                        repository.WriteOutput("System", error, 0);
                        MessageBox.Show(
                            $"Error generating documentation:\n\n{error}\n\nSee Output window for details.",
                            "EA Doc Generator",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Error);
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error running documentation generator:\n\n{ex.Message}\n\nMake sure Python is installed and in your PATH.",
                    "EA Doc Generator",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
        }

        /// <summary>
        /// Extract diagrams using the Windows-specific COM automation
        /// </summary>
        private void ExtractDiagrams()
        {
            try
            {
                string scriptDir = GetScriptDirectory();
                string pythonScript = Path.Combine(scriptDir, "ea_diagram_extractor.py");
                string outputDir = Path.Combine(scriptDir, "diagrams");

                if (!System.IO.File.Exists(pythonScript))
                {
                    MessageBox.Show($"Diagram extractor script not found at: {pythonScript}",
                        "EA Doc Generator", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return;
                }

                // Build command line
                string args = $"\"{pythonScript}\" --output-dir \"{outputDir}\"";

                // Execute Python script
                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = args,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    WorkingDirectory = scriptDir
                };

                repository.WriteOutput("System", "EA Doc Generator: Extracting diagrams...", 0);

                using (Process process = Process.Start(startInfo))
                {
                    string output = process.StandardOutput.ReadToEnd();
                    string error = process.StandardError.ReadToEnd();
                    process.WaitForExit();

                    if (process.ExitCode == 0)
                    {
                        repository.WriteOutput("System", "EA Doc Generator: Diagrams extracted successfully!", 0);
                        repository.WriteOutput("System", output, 0);
                        MessageBox.Show(
                            $"Diagrams extracted successfully!\n\nOutput location: {outputDir}",
                            "EA Doc Generator",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Information);
                    }
                    else
                    {
                        repository.WriteOutput("System", "EA Doc Generator: Error extracting diagrams", 0);
                        repository.WriteOutput("System", error, 0);
                        MessageBox.Show(
                            $"Error extracting diagrams:\n\n{error}\n\nNote: This feature requires Windows and pywin32.",
                            "EA Doc Generator",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Error);
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error extracting diagrams:\n\n{ex.Message}",
                    "EA Doc Generator",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
        }

        /// <summary>
        /// Open the output folder in file explorer
        /// </summary>
        private void OpenOutputFolder()
        {
            try
            {
                string scriptDir = GetScriptDirectory();
                string outputDir = Path.Combine(scriptDir, "docs");

                if (Directory.Exists(outputDir))
                {
                    Process.Start("explorer.exe", outputDir);
                }
                else
                {
                    MessageBox.Show(
                        $"Output folder not found: {outputDir}\n\nPlease generate documentation first.",
                        "EA Doc Generator",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error opening output folder:\n\n{ex.Message}",
                    "EA Doc Generator",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
        }

        /// <summary>
        /// Show settings dialog
        /// </summary>
        private void ShowSettings()
        {
            try
            {
                string scriptDir = GetScriptDirectory();
                string configPath = Path.Combine(scriptDir, "config.yaml");

                if (System.IO.File.Exists(configPath))
                {
                    Process.Start("notepad.exe", configPath);
                }
                else
                {
                    MessageBox.Show(
                        $"Config file not found: {configPath}",
                        "EA Doc Generator",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error opening settings:\n\n{ex.Message}",
                    "EA Doc Generator",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
        }

        /// <summary>
        /// Show about dialog
        /// </summary>
        private void ShowAbout()
        {
            MessageBox.Show(
                "EA Documentation Generator Addin\n\n" +
                "Version 1.0.0\n\n" +
                "Generate comprehensive documentation from your EA models without leaving Enterprise Architect.\n\n" +
                "Features:\n" +
                "• Generate use case documentation\n" +
                "• Generate class diagrams and documentation\n" +
                "• Generate component documentation\n" +
                "• Generate state machine documentation\n" +
                "• Generate requirements documentation\n" +
                "• Extract diagrams directly from EA (Windows)\n" +
                "• Quality reports and dependency analysis\n\n" +
                "For more information, see README.md",
                "About EA Doc Generator",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information);
        }

        /// <summary>
        /// Check if menu item should be enabled
        /// </summary>
        public bool EA_GetMenuState(Repository repository, string location, string menuName, string itemName, ref bool isEnabled, ref bool isChecked)
        {
            // All menu items are always enabled
            isEnabled = true;
            isChecked = false;
            return true;
        }
    }
}
