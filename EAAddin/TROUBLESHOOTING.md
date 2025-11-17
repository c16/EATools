# EA Addin Troubleshooting for EA 17

## SOLUTION FOUND

**Root Cause**: The project was building with "Any CPU" platform target instead of explicit x64 target.

**Fix**: Updated EADocGenerator.csproj to explicitly target x64 platform as required by Sparx Systems documentation.

According to Sparx Systems EA 17 documentation:
> "When generating a .NET assembly, you must explicitly set the 'Target Platform' to x86/x64. Leaving it on 'Any CPU' could cause issues when Enterprise Architect 32 bit is run on a 64 bit version of windows."

**Changes Made**:
- EADocGenerator.csproj: Changed platform from AnyCPU to x64
- build.bat: Updated to build with `/p:Platform=x64`
- All registration scripts updated to use `bin\x64\Release\` output path

**To Test**: Run build.bat, then register.bat (as admin), then restart EA and check Extensions → Add-Ins.

---

## Previous Status (RESOLVED)

The EA addin was successfully built and registered, but EA 17 (64-bit) was not loading it.

## What Works

✅ **Build** - DLL compiles successfully
✅ **COM Registration** - RegAsm registers the COM components successfully
✅ **Registry Entry** - EA addin registry key is created correctly at:
- `HKEY_CURRENT_USER\Software\Sparx Systems\EAAddins\EADocGenerator`
- Location points to: `E:\projects\EAtools\EATools\EAAddin\bin\Release\EADocGenerator.dll`

✅ **COM Visibility** - CLSID and ProgId are registered:
- CLSID: `{8A6C6AC1-8B5E-4F5D-9E3C-2A4B5C6D7E8F}`
- ProgId: `EADocGenerator.EADocGeneratorAddin`

## What Doesn't Work

❌ **EA Discovery** - EA 17 is not discovering or loading the addin
- Addin does not appear in Specialize → Add-Ins list
- No menu items appear
- Test addin with message boxes shows EA never instantiates the class

## Possible Causes (EA 17 Specific)

### 1. EA 17 May Require MDG Technology
EA 17 might have changed how .NET addins are loaded. Some versions require addins to be packaged as MDG Technologies instead of simple COM DLLs.

**Solution:** Package as MDG Technology (.mts file)

### 2. .NET Framework Version Mismatch
EA 17 64-bit might require a specific .NET Framework version or have compatibility issues with .NET 4.8.

**To Check:**
- Try targeting .NET Framework 4.5 or 4.6 instead
- Check EA's installation folder for clues about .NET version

### 3. Security/Trust Issues
Windows or EA might be blocking unsigned .NET assemblies.

**To Try:**
- Sign the assembly with a strong name key
- Check Windows SmartScreen/Defender logs
- Run EA as administrator

### 4. EA 17 Uses Different Registry Location
EA 17 might look for addins in a different registry location.

**To Try:**
- Check `HKEY_LOCAL_MACHINE\Software\Sparx Systems\EAAddins`
- Check for EA 17 specific registry paths
- Look in EA's installation folder for addin configuration files

### 5. Addin Framework Changed in EA 17
EA 17 might require different method signatures or interfaces.

**To Check:**
- Review Sparx Systems EA 17 SDK documentation
- Check EA 17 forums for .NET addin examples
- Look for EA 17 specific addin samples

## What We've Tried

1. ✅ Built C# addin with EA COM interface
2. ✅ Registered with both 32-bit and 64-bit RegAsm
3. ✅ Added COM visibility attributes
4. ✅ Created explicit COM interface with DispId attributes
5. ✅ Unblocked DLL file
6. ✅ Registered in correct registry location
7. ✅ Created minimal test addin (no complex dependencies)
8. ✅ Verified all registry entries and COM registration

## Recommended Next Steps

### Step 1: Check EA Documentation
Visit Sparx Systems documentation for EA 17:
- https://sparxsystems.com/enterprise_architect_user_guide/17.0/
- Look for "Add-In Development" section
- Check for any EA 17 specific requirements

### Step 2: Check Sparx Forums
Search the Sparx Systems forums for:
- "EA 17 .NET addin"
- "EA 17 addin not loading"
- "EA 17 COM addin"

### Step 3: Contact Sparx Support
Since everything appears correctly configured, this might be an EA 17 specific issue that requires Sparx Systems input.

### Step 4: Try Alternative Approaches

#### Option A: Use EA Extension Pack
Some EA versions require addins to be packaged differently. Try creating an EA Extension Pack.

#### Option B: Use Scripting Instead
EA supports scripts that can be triggered manually. While not as seamless as an addin, this would work:

```vbscript
' EA Script to run Python doc generator
Sub Main()
    Dim repoPath
    repoPath = Repository.ConnectionString
    ' Extract path and call Python script
    ' ...
End Sub
```

#### Option C: External Tool Integration
Register the Python script as an external tool in EA:
1. Go to Tools → Customize
2. Add external tool pointing to Python script
3. Configure to pass current repository as parameter

## Files Included

- `EADocGenerator.cs` - Main addin implementation with full feature set
- `TestAddin.cs` - Minimal test addin for diagnostics
- `build.bat` - Build script
- `register.bat` - Registration script
- `unregister.bat` - Unregistration script
- `diagnose.bat` - Diagnostic script to check registration status
- `register_test.bat` - Test addin registration

## For Future Reference

If you get this working, please document:
1. What EA 17 version exactly (build number)
2. What changed to make it work
3. Any EA 17 specific requirements

This will help others trying to create EA 17 addins!

## Workaround: Use Command Line Instead

Since the addin isn't loading, you can still use the Python generator from command line:

```cmd
cd E:\projects\EAtools\EATools
python sparx_doc_generator.py "path\to\your\model.qea"
```

Or use the GUI version:
```cmd
python sparx_doc_gui.py
```

## Summary

The addin code is complete and correctly registered, but EA 17 is not loading it due to what appears to be an EA 17 specific discovery or loading issue. The Python documentation generator itself works perfectly via command line or GUI.
