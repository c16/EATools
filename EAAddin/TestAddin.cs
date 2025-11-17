using System;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace EADocGenerator
{
    [ComVisible(true)]
    [Guid("9C7D6AC1-8B5E-4F5D-9E3C-2A4B5C6D7E8F")]
    [ProgId("EADocGenerator.TestAddin")]
    [ClassInterface(ClassInterfaceType.AutoDual)]
    public class TestAddin
    {
        public TestAddin()
        {
            MessageBox.Show("TestAddin constructor called!", "EA Test");
        }

        public string EA_Connect(object repository)
        {
            MessageBox.Show("EA_Connect called!", "EA Test");
            return "Test Addin";
        }

        public void EA_Disconnect()
        {
        }

        public object EA_GetMenuItems(object repository, string location, string menuName)
        {
            if (menuName == "")
                return "-&Test Menu";
            if (menuName == "-&Test Menu")
                return new string[] { "&Test Item" };
            return "";
        }

        public void EA_MenuClick(object repository, string location, string menuName, string itemName)
        {
            MessageBox.Show("Menu clicked: " + itemName, "EA Test");
        }

        public bool EA_GetMenuState(object repository, string location, string menuName, string itemName, ref bool isEnabled, ref bool isChecked)
        {
            isEnabled = true;
            return true;
        }
    }
}
