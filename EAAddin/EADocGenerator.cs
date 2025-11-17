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
        private const string MENU_GENERATE_ALL_HTML = "Generate All Documentation (&HTML)";
        private const string MENU_GENERATE_USE_CASES = "Generate &Use Cases";
        private const string MENU_GENERATE_CLASSES = "Generate &Classes";
        private const string MENU_GENERATE_COMPONENTS = "Generate C&omponents";
        private const string MENU_GENERATE_STATE_MACHINES = "Generate &State Machines";
        private const string MENU_GENERATE_REQUIREMENTS = "Generate &Requirements";
        private const string MENU_EXTRACT_DIAGRAMS = "Extract &Diagrams (Windows Only)";
        private const string MENU_OPEN_OUTPUT = "&Open Output Folder";
        private const string MENU_OPEN_HTML_OUTPUT = "Open &HTML Output Folder";
        private const string MENU_SETTINGS = "&Settings";
        private const string MENU_ABOUT = "&About";

        /// <summary>
        /// Public constructor required for COM
        /// </summary>
        public EADocGeneratorAddin()
        {
        }

        /// <summary>
        /// Called when EA starts - initialize the addin
        /// </summary>
        public string EA_Connect(Repository repository)
        {
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
                        MENU_GENERATE_ALL_HTML,
                        "-",
                        MENU_GENERATE_USE_CASES,
                        MENU_GENERATE_CLASSES,
                        MENU_GENERATE_COMPONENTS,
                        MENU_GENERATE_STATE_MACHINES,
                        MENU_GENERATE_REQUIREMENTS,
                        "-",
                        MENU_EXTRACT_DIAGRAMS,
                        "-",
                        MENU_OPEN_OUTPUT,
                        MENU_OPEN_HTML_OUTPUT,
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
                    GenerateDocumentation("all", false);
                    break;
                case MENU_GENERATE_ALL_HTML:
                    GenerateDocumentation("all", true);
                    break;
                case MENU_GENERATE_USE_CASES:
                    GenerateDocumentation("use-cases", false);
                    break;
                case MENU_GENERATE_CLASSES:
                    GenerateDocumentation("classes", false);
                    break;
                case MENU_GENERATE_COMPONENTS:
                    GenerateDocumentation("components", false);
                    break;
                case MENU_GENERATE_STATE_MACHINES:
                    GenerateDocumentation("state-machines", false);
                    break;
                case MENU_GENERATE_REQUIREMENTS:
                    GenerateDocumentation("requirements", false);
                    break;
                case MENU_EXTRACT_DIAGRAMS:
                    ExtractDiagrams();
                    break;
                case MENU_OPEN_OUTPUT:
                    OpenOutputFolder();
                    break;
                case MENU_OPEN_HTML_OUTPUT:
                    OpenHtmlOutputFolder();
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
        /// Assumes the addin DLL is in EATools/EAAddin/bin/x64/Release/ folder
        /// </summary>
        private string GetScriptDirectory()
        {
            string addinPath = System.Reflection.Assembly.GetExecutingAssembly().Location;
            // DLL is in: EATools/EAAddin/bin/x64/Release/EADocGenerator.dll
            // Need to go up 5 levels: Release -> x64 -> bin -> EAAddin -> EATools
            string eaToolsPath = Path.GetFullPath(Path.Combine(Path.GetDirectoryName(addinPath), "..", "..", "..", ".."));
            return eaToolsPath;
        }

        /// <summary>
        /// Generate documentation using Python script
        /// </summary>
        private void GenerateDocumentation(string docType, bool generateHtml)
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
                string htmlOutputDir = Path.Combine(scriptDir, "docs_html");

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

                // Add HTML generation flag if requested
                if (generateHtml)
                {
                    args += $" --html --html-output \"{htmlOutputDir}\"";
                }

                // Show progress message
                string format = generateHtml ? "Markdown + HTML" : "Markdown";
                repository.WriteOutput("System", $"EA Doc Generator: Starting documentation generation ({docType}, {format})...", 0);
                repository.WriteOutput("System", $"Command: python {args}", 0);

                // Create log file for output
                string logFile = Path.Combine(scriptDir, "ea_addin_output.log");

                // Execute Python script in the background with output redirected to log file
                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = args,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    WorkingDirectory = scriptDir,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true
                };

                Process process = Process.Start(startInfo);

                // Asynchronously read output and write to log file
                System.Threading.Tasks.Task.Run(() =>
                {
                    try
                    {
                        using (var logWriter = new System.IO.StreamWriter(logFile, false))
                        {
                            logWriter.WriteLine($"=== EA Doc Generator Log - {DateTime.Now} ===");
                            logWriter.WriteLine($"Command: python {args}");
                            logWriter.WriteLine($"Working Directory: {scriptDir}");
                            logWriter.WriteLine();
                            logWriter.WriteLine("=== STDOUT ===");
                            logWriter.WriteLine(process.StandardOutput.ReadToEnd());
                            logWriter.WriteLine();
                            logWriter.WriteLine("=== STDERR ===");
                            logWriter.WriteLine(process.StandardError.ReadToEnd());
                            logWriter.WriteLine();
                            logWriter.WriteLine($"Exit Code: {process.ExitCode}");
                        }
                    }
                    catch { }
                });

                // Show notification that generation started
                string outputInfo = generateHtml
                    ? $"Markdown: {outputDir}\nHTML: {htmlOutputDir}"
                    : $"Markdown: {outputDir}";

                MessageBox.Show(
                    $"Documentation generation started in the background.\n\n" +
                    $"Type: {docType}\n" +
                    $"Format: {format}\n" +
                    $"Output:\n{outputInfo}\n\n" +
                    $"You can continue working in EA. Check the output folder when complete.",
                    "EA Doc Generator",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information);
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

                repository.WriteOutput("System", "EA Doc Generator: Starting diagram extraction...", 0);
                repository.WriteOutput("System", $"Command: python {args}", 0);

                // Execute Python script in the background (don't block EA)
                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = args,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    WorkingDirectory = scriptDir
                };

                Process.Start(startInfo);

                // Show notification
                MessageBox.Show(
                    $"Diagram extraction started in the background.\n\n" +
                    $"Output: {outputDir}\n\n" +
                    $"Note: This requires EA to remain open while diagrams are being extracted.\n" +
                    $"You can continue working in EA.",
                    "EA Doc Generator",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information);
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
        /// Open the HTML output folder in file explorer
        /// </summary>
        private void OpenHtmlOutputFolder()
        {
            try
            {
                string scriptDir = GetScriptDirectory();
                string htmlOutputDir = Path.Combine(scriptDir, "docs_html");

                if (Directory.Exists(htmlOutputDir))
                {
                    Process.Start("explorer.exe", htmlOutputDir);
                }
                else
                {
                    MessageBox.Show(
                        $"HTML output folder not found: {htmlOutputDir}\n\nPlease generate HTML documentation first using 'Generate All Documentation (HTML)'.",
                        "EA Doc Generator",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error opening HTML output folder:\n\n{ex.Message}",
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
