---
name: dotnet-packaging-msix
description: Use when packaging a .NET 10 WPF application as MSIX for enterprise or store distribution — setting up the packaging project, configuring Package.appxmanifest, code signing with signtool.exe, GPO silent deployment, AppInstaller auto-update, or wiring up a GitHub Actions CI/CD pipeline to build and sign MSIX. Windows Installer / WiX / MSI is out of scope for this skill.
---

# .NET 10 WPF — MSIX Packaging & Distribution

## Overview

MSIX is the modern Windows packaging format. It installs cleanly, updates atomically, and supports enterprise deployment via GPO/Intune. WiX/MSI is out of scope — MSIX only.

**Core rule:** The packaging project is a thin wrapper. All build logic stays in the main `.csproj`; the packaging project only controls manifest and signing.

---

## Project Structure

```
MyApp.sln
  MyApp/                        ← main WPF project
  MyApp.Package/                ← Windows Application Packaging Project (.wapproj)
    Package.appxmanifest
    MyApp.Package.wapproj
```

Add the packaging project via Visual Studio: **Add > New Project > Windows Application Packaging Project**.

---

## Package.appxmanifest — Required Settings

```xml
<!-- Package element must declare the rescap namespace for runFullTrust -->
<Package
  xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
  xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"
  IgnorableNamespaces="rescap">

  <Identity
    Name="MyCompany.MyApp"
    Publisher="CN=MyCompany, O=MyCompany, C=JP"
    Version="1.2.0.0" />          <!-- Must be 4-part: major.minor.build.revision -->

  <Properties>
    <DisplayName>My App</DisplayName>
    <PublisherDisplayName>MyCompany</PublisherDisplayName>
    <Logo>Assets\StoreLogo.png</Logo>
  </Properties>

  <Capabilities>
    <rescap:Capability Name="runFullTrust" />   <!-- Required for WPF -->
  </Capabilities>

</Package>
```

**Version sync:** Keep `Version` here in sync with your application version. A mismatch causes update failures. Automate via MSBuild property:

```xml
<!-- MyApp.Package.wapproj — $(Version) is a 3-part semver; append .0 for required 4-part MSIX format -->
<PackageVersion>$(Version).0</PackageVersion>
```

---

## Code Signing

### Development (self-signed)
```powershell
# Create cert
New-SelfSignedCertificate -Type CodeSigningCert `
  -Subject "CN=MyCompany, O=MyCompany, C=JP" `
  -KeyUsage DigitalSignature -FriendlyName "MyApp Dev" `
  -CertStoreLocation Cert:\CurrentUser\My `
  -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

# Export to pfx
$cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -match "MyCompany" }
Export-PfxCertificate -Cert $cert -FilePath MyApp.pfx -Password (ConvertTo-SecureString -String "pass" -Force -AsPlainText)
```

### Production (EV certificate)
Use an EV Code Signing certificate from a CA (DigiCert, Sectigo). Required for SmartScreen trust without user warning.

```powershell
# Sign with signtool
signtool sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 `
  /f cert.pfx /p $env:CERT_PASSWORD `
  MyApp.Package_1.2.0.0_x64.msix
```

---

## Enterprise Deployment (GPO / Intune)

### GPO Silent Install
```powershell
# Deploy to machines via GPO startup script
Add-AppxProvisionedPackage -Online `
  -PackagePath "\\share\MyApp_1.2.0.0_x64.msix" `
  -SkipLicense

# Or per-user (no elevation required)
Add-AppxPackage -Path "\\share\MyApp_1.2.0.0_x64.msix"
```

**Prerequisite:** The signing certificate must be in the machine's Trusted People / Trusted Root store via GPO before deployment.

### Intune
Upload the `.msix` as a Line-of-Business (LOB) app. Intune handles silent install and update.

---

## Auto-Update (AppInstaller)

Create `MyApp.appinstaller` alongside the MSIX on your distribution share:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AppInstaller Uri="https://releases.mycompany.com/MyApp.appinstaller"
              Version="1.2.0.0"
              xmlns="http://schemas.microsoft.com/appx/appinstaller/2018">
  <MainPackage Name="MyCompany.MyApp"
               Version="1.2.0.0"
               Publisher="CN=MyCompany, O=MyCompany, C=JP"
               Uri="https://releases.mycompany.com/MyApp_1.2.0.0_x64.msix" />
  <UpdateSettings>
    <OnLaunch HoursBetweenUpdateChecks="12" UpdateBlocksActivation="false" />
  </UpdateSettings>
</AppInstaller>
```

**Update while running:** Windows will notify users of a pending update; the app restarts cleanly on next launch. For forced restart logic, use `PackageManager`:

```csharp
// Check and trigger update programmatically
var pm = new PackageManager();
var package = pm.FindPackagesForUser("").FirstOrDefault(p =>
    p.Id.FamilyName.StartsWith("MyCompany.MyApp"));
// Prompt user to restart when update is available
```

---

## GitHub Actions CI/CD

```yaml
# .github/workflows/release.yml
name: Build & Sign MSIX

on:
  push:
    tags: ["v*"]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '10.0.x'

      - name: Decode certificate
        run: |
          $bytes = [Convert]::FromBase64String("${{ secrets.CERT_BASE64 }}")
          [IO.File]::WriteAllBytes("cert.pfx", $bytes)

      - name: Build MSIX
        run: |
          msbuild MyApp.Package/MyApp.Package.wapproj `
            /p:Configuration=Release `
            /p:AppxPackageSigningEnabled=false `
            /p:AppxBundlePlatforms=x64

      - name: Sign
        run: |
          signtool sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 `
            /f cert.pfx /p "${{ secrets.CERT_PASSWORD }}" `
            MyApp.Package/AppPackages/**/*.msix

      - name: Upload release asset
        uses: softprops/action-gh-release@v2
        with:
          files: MyApp.Package/AppPackages/**/*.msix
```

**Secret management:** Store `CERT_BASE64` (base64-encoded PFX) and `CERT_PASSWORD` in GitHub repository secrets. Never commit the PFX.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `CERT_TRUST_FAILED_AN_UNKNOWN_CA` on install | Install the signing cert into Trusted Root / Trusted People via GPO first |
| Version `1.0.0` (3-part) fails | MSIX requires 4-part version: `1.0.0.0` |
| `runFullTrust` capability missing | WPF apps need it — add to `<Capabilities>` |
| Update fails silently | Ensure AppInstaller `Uri` attribute matches the exact hosted URL |
| CI build succeeds but MSIX is unsigned | `AppxPackageSigningEnabled=false` + explicit signtool step required |

---

## Quick Reference

| Task | How |
|------|-----|
| Add packaging project | VS: Add > New Project > Windows Application Packaging Project |
| Required manifest namespace | `xmlns:rescap` + `IgnorableNamespaces="rescap"` on `<Package>` |
| Version format | 4-part `major.minor.build.revision`; automate with `$(Version).0` |
| Development signing | `New-SelfSignedCertificate` + `Export-PfxCertificate` |
| Production signing | EV cert from CA + `signtool sign /fd SHA256 /tr <timestamp-url>` |
| GPO silent install | `Add-AppxProvisionedPackage` (machine) or `Add-AppxPackage` (user) |
| Auto-update | `.appinstaller` file + `OnLaunch HoursBetweenUpdateChecks` |
| CI/CD | msbuild `.wapproj` with `AppxPackageSigningEnabled=false`, then signtool |
