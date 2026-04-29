# .NET 10 WPF — GitHub Actions で MSIX ビルド・署名して Release に添付する完全ガイド

---

## 1. 前提: プロジェクト構造

```
MyApp.sln
  MyApp/                        ← メイン WPF プロジェクト
  MyApp.Package/                ← Windows Application Packaging Project
    Package.appxmanifest
    MyApp.Package.wapproj
```

Visual Studio で **Add > New Project > Windows Application Packaging Project** を追加します。

---

## 2. Package.appxmanifest の必須設定

```xml
<Identity
  Name="com.mycompany.myapp"
  Publisher="CN=MyCompany, O=MyCompany, C=JP"
  Version="1.2.0.0" />  <!-- 必ず 4 パート: major.minor.build.revision -->

<Properties>
  <DisplayName>My App</DisplayName>
  <PublisherDisplayName>MyCompany</PublisherDisplayName>
  <Logo>Assets\StoreLogo.png</Logo>
</Properties>

<Capabilities>
  <rescap:Capability Name="runFullTrust" />  <!-- WPF には必須 -->
</Capabilities>
```

> **注意:** Version は 3 パート (`1.0.0`) だと MSIX がインストール失敗します。必ず `1.0.0.0` の 4 パートにしてください。

バージョンを AssemblyVersion と自動同期する場合は `.wapproj` に以下を追加します:

```xml
<PackageVersion>$(AssemblyVersion).0</PackageVersion>
```

---

## 3. PFX 証明書を GitHub Secrets に保存する手順

### 3-1. 証明書を Base64 エンコードする

**開発用 自己署名証明書を作る場合 (PowerShell):**

```powershell
# 証明書を作成
New-SelfSignedCertificate -Type CodeSigningCert `
  -Subject "CN=MyCompany, O=MyCompany, C=JP" `
  -KeyUsage DigitalSignature `
  -FriendlyName "MyApp Dev" `
  -CertStoreLocation Cert:\CurrentUser\My `
  -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

# PFX にエクスポート
$cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -match "MyCompany" }
Export-PfxCertificate -Cert $cert -FilePath MyApp.pfx `
  -Password (ConvertTo-SecureString -String "YourPassword" -Force -AsPlainText)
```

**本番用 EV 証明書の場合:** DigiCert / Sectigo から取得した `.pfx` ファイルをそのまま使います。

### 3-2. PFX を Base64 文字列に変換

```powershell
# Windows PowerShell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("MyApp.pfx")) | Set-Clipboard
```

```bash
# macOS / Linux
base64 -i MyApp.pfx | pbcopy   # macOS
base64 -w 0 MyApp.pfx          # Linux (stdout に出力)
```

### 3-3. GitHub Secrets に登録

GitHub リポジトリの **Settings > Secrets and variables > Actions > New repository secret** で以下を登録します:

| Secret 名       | 値                                  |
|----------------|-------------------------------------|
| `CERT_BASE64`  | 上でコピーした Base64 文字列全体      |
| `CERT_PASSWORD`| PFX の Export 時に設定したパスワード  |

> **絶対に PFX ファイルをリポジトリにコミットしてはいけません。** `.gitignore` に `*.pfx` を追加してください。

---

## 4. 完全な GitHub Actions Workflow YAML

```yaml
# .github/workflows/release.yml
name: Build & Sign MSIX

on:
  push:
    tags:
      - "v*"   # v1.2.0 のようなタグで起動

jobs:
  build:
    runs-on: windows-latest

    steps:
      # ─────────────────────────────────────────
      # 1. ソースチェックアウト
      # ─────────────────────────────────────────
      - name: Checkout
        uses: actions/checkout@v4

      # ─────────────────────────────────────────
      # 2. .NET 10 セットアップ
      # ─────────────────────────────────────────
      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '10.0.x'

      # ─────────────────────────────────────────
      # 3. PFX 証明書を Secrets から復元
      #    CERT_BASE64 → cert.pfx に書き出す
      # ─────────────────────────────────────────
      - name: Decode certificate
        shell: pwsh
        run: |
          $bytes = [Convert]::FromBase64String("${{ secrets.CERT_BASE64 }}")
          [IO.File]::WriteAllBytes("${{ github.workspace }}\cert.pfx", $bytes)

      # ─────────────────────────────────────────
      # 4. タグからバージョン番号を抽出
      #    (v1.2.3 → 1.2.3.0)
      # ─────────────────────────────────────────
      - name: Extract version
        id: version
        shell: pwsh
        run: |
          $tag = "${{ github.ref_name }}"          # 例: v1.2.3
          $ver = $tag.TrimStart("v") + ".0"        # → 1.2.3.0
          echo "APP_VERSION=$ver" >> $env:GITHUB_ENV

      # ─────────────────────────────────────────
      # 5. WPF プロジェクトをパブリッシュ
      # ─────────────────────────────────────────
      - name: Publish WPF app
        shell: pwsh
        run: |
          dotnet publish MyApp/MyApp.csproj `
            -c Release `
            -r win-x64 `
            --self-contained true `
            -p:PublishSingleFile=false

      # ─────────────────────────────────────────
      # 6. MSIX パッケージをビルド
      #    AppxPackageSigningEnabled=false で
      #    msbuild 内部の署名をスキップし、
      #    次のステップで signtool を使う
      # ─────────────────────────────────────────
      - name: Build MSIX
        shell: pwsh
        run: |
          msbuild MyApp.Package/MyApp.Package.wapproj `
            /p:Configuration=Release `
            /p:AppxPackageSigningEnabled=false `
            /p:AppxBundlePlatforms=x64 `
            /p:AppxPackageDir="${{ github.workspace }}\AppPackages\\" `
            /p:PackageVersion=${{ env.APP_VERSION }}

      # ─────────────────────────────────────────
      # 7. signtool で署名 + タイムスタンプ
      # ─────────────────────────────────────────
      - name: Sign MSIX with signtool
        shell: pwsh
        run: |
          $msixFiles = Get-ChildItem `
            -Path "${{ github.workspace }}\AppPackages" `
            -Filter "*.msix" `
            -Recurse
          foreach ($file in $msixFiles) {
            signtool sign `
              /fd SHA256 `
              /tr http://timestamp.digicert.com `
              /td SHA256 `
              /f "${{ github.workspace }}\cert.pfx" `
              /p "${{ secrets.CERT_PASSWORD }}" `
              $file.FullName
            Write-Host "Signed: $($file.FullName)"
          }

      # ─────────────────────────────────────────
      # 8. 署名を検証 (オプションだが推奨)
      # ─────────────────────────────────────────
      - name: Verify signature
        shell: pwsh
        run: |
          Get-ChildItem `
            -Path "${{ github.workspace }}\AppPackages" `
            -Filter "*.msix" `
            -Recurse |
          ForEach-Object {
            signtool verify /pa /v $_.FullName
          }

      # ─────────────────────────────────────────
      # 9. cert.pfx をクリーンアップ
      #    (ランナーのディスクに残さない)
      # ─────────────────────────────────────────
      - name: Cleanup certificate
        if: always()
        shell: pwsh
        run: Remove-Item -Path "${{ github.workspace }}\cert.pfx" -Force -ErrorAction SilentlyContinue

      # ─────────────────────────────────────────
      # 10. GitHub Release に MSIX を添付
      # ─────────────────────────────────────────
      - name: Upload to GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          files: AppPackages/**/*.msix
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 5. よくあるミスと対処

| エラー / 症状 | 原因 | 対処 |
|---|---|---|
| `CERT_TRUST_FAILED_AN_UNKNOWN_CA` | 受信側マシンが署名 CA を信頼していない | GPO で Trusted Root / Trusted People に証明書を配布 |
| Version `1.0.0` でインストール失敗 | MSIX は 4 パートのバージョンが必須 | `1.0.0.0` に変更 |
| `runFullTrust` がない | WPF に必須の Capability が未追加 | `Package.appxmanifest` に追加 |
| CI で MSIX が unsigned | `AppxPackageSigningEnabled` の設定ミス | `false` にして signtool ステップを明示的に実行 |
| SmartScreen 警告が出る | EV 証明書でない | DigiCert / Sectigo の EV Code Signing 証明書を使用 |
| signtool が見つからない | `windows-latest` ランナーには含まれている | パスが通らない場合は `windows-sdk-version` を明示 |

---

## 6. セキュリティ上の注意点

- `cert.pfx` は **絶対にリポジトリにコミットしない**。`.gitignore` に `*.pfx` を追加。
- `CERT_BASE64` と `CERT_PASSWORD` は **GitHub Repository Secrets** (または Environment Secrets) にのみ保存。
- Workflow 完了後にランナー上の `cert.pfx` をステップ 9 (`if: always()`) で削除する。
- 本番環境では自己署名証明書ではなく **EV Code Signing 証明書** を使用し、SmartScreen の信頼を確立する。

---

## 7. AppInstaller による自動更新 (オプション)

MSIX と一緒に `MyApp.appinstaller` を GitHub Release や配布サーバーに置くと、ユーザーが次回起動時に自動更新を受け取れます:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AppInstaller Uri="https://releases.mycompany.com/MyApp.appinstaller"
              Version="1.2.0.0"
              xmlns="http://schemas.microsoft.com/appx/appinstaller/2018">
  <MainPackage Name="com.mycompany.myapp"
               Version="1.2.0.0"
               Publisher="CN=MyCompany, O=MyCompany, C=JP"
               Uri="https://releases.mycompany.com/MyApp_1.2.0.0_x64.msix" />
  <UpdateSettings>
    <OnLaunch HoursBetweenUpdateChecks="12" UpdateBlocksActivation="false" />
  </UpdateSettings>
</AppInstaller>
```
