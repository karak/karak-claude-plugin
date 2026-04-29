# .NET 10 WPF — GitHub Actions で MSIX ビルド・署名して Release に添付する完全手順

---

## 1. 前提・全体構成

| 項目 | 内容 |
|------|------|
| ターゲット | .NET 10 WPF、Windows Packaging Project（.wapproj）で MSIX を生成 |
| 署名方式 | PFX（PKCS#12）→ Base64 エンコードして GitHub Secrets に保存 → `signtool.exe` で署名 |
| ランナー | `windows-latest`（Windows Server 2025 相当、SDK 10 対応） |
| トリガー | `v*` タグプッシュ → GitHub Release を自動作成して `.msix` / `.msixbundle` を添付 |

---

## 2. PFX 証明書を GitHub Secrets に保存する

### 2-1. PFX を Base64 文字列に変換

**PowerShell（Windows）:**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("MyCert.pfx")) | Set-Clipboard
```

**bash（macOS / Linux）:**
```bash
base64 -w 0 MyCert.pfx | pbcopy   # macOS
base64 -w 0 MyCert.pfx            # Linux — 出力をコピー
```

### 2-2. Secrets に登録

GitHub リポジトリ → **Settings → Secrets and variables → Actions → New repository secret**

| Secret 名 | 値 |
|-----------|-----|
| `SIGN_CERTIFICATE_BASE64` | 上記の Base64 文字列 |
| `SIGN_CERTIFICATE_PASSWORD` | PFX のパスワード（無い場合は空文字でも登録） |

> **セキュリティ注意点**
> - PFX ファイル自体はリポジトリにコミットしない。
> - Secrets は `Environment` を使ってステージング／本番で分けることを推奨。

---

## 3. プロジェクト構成の前提

```
MySolution/
├── MySolution.sln
├── MyWpfApp/
│   ├── MyWpfApp.csproj        # .NET 10 WPF
│   └── ...
└── MyWpfApp.Package/
    ├── MyWpfApp.Package.wapproj   # Windows Application Packaging Project
    └── Package.appxmanifest
```

`Package.appxmanifest` の `<Identity Publisher="...">` は証明書の **Subject** と一致させること。

---

## 4. 完全な workflow YAML

```yaml
# .github/workflows/release-msix.yml
name: Release MSIX

on:
  push:
    tags:
      - "v*"          # v1.0.0 など semver タグで起動

permissions:
  contents: write     # GitHub Release の作成・アセット添付に必要

env:
  DOTNET_VERSION: "10.0.x"
  SOLUTION_PATH: MySolution/MySolution.sln
  WAP_PROJECT_PATH: MySolution/MyWpfApp.Package/MyWpfApp.Package.wapproj
  APP_PACKAGES_DIR: MySolution/MyWpfApp.Package/AppPackages
  # 署名後の msix/msixbundle を置くディレクトリ（後工程で利用）
  SIGNED_OUTPUT_DIR: SignedOutput

jobs:
  build-sign-release:
    name: Build, Sign, and Release
    runs-on: windows-latest

    steps:
      # ───────────────────────────────────────────
      # 1. ソースチェックアウト
      # ───────────────────────────────────────────
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0        # タグ情報も取得

      # ───────────────────────────────────────────
      # 2. .NET 10 SDK セットアップ
      # ───────────────────────────────────────────
      - name: Setup .NET ${{ env.DOTNET_VERSION }}
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: ${{ env.DOTNET_VERSION }}

      # ───────────────────────────────────────────
      # 3. NuGet パッケージ復元
      #    wapproj は msbuild の restore で処理
      # ───────────────────────────────────────────
      - name: Restore NuGet packages
        run: |
          dotnet restore "${{ env.SOLUTION_PATH }}"

      # ───────────────────────────────────────────
      # 4. MSIX ビルド（未署名）
      #    AppxPackageSigningEnabled=false で署名をスキップ
      #    → 後工程で signtool を使う
      # ───────────────────────────────────────────
      - name: Build MSIX (unsigned)
        shell: pwsh
        run: |
          $version = "${{ github.ref_name }}" -replace '^v', ''   # "1.2.3"
          # semver を 4 桁に変換（例: 1.2.3 → 1.2.3.0）
          $parts = $version.Split('.')
          while ($parts.Count -lt 4) { $parts += '0' }
          $msiVersion = $parts[0..3] -join '.'

          msbuild "${{ env.WAP_PROJECT_PATH }}" `
            /p:Configuration=Release `
            /p:Platform=x64 `
            /p:UapAppxPackageBuildMode=StoreUpload `
            /p:AppxBundle=Always `
            /p:AppxBundlePlatforms="x64" `
            /p:AppxPackageSigningEnabled=false `
            /p:AppxPackageDir="${{ env.APP_PACKAGES_DIR }}/" `
            /p:Version=$msiVersion `
            /p:GenerateAppxPackageOnBuild=true `
            /restore

      # ───────────────────────────────────────────
      # 5. PFX をディスクに復元（一時ファイル）
      # ───────────────────────────────────────────
      - name: Decode and write PFX
        shell: pwsh
        run: |
          $certBytes = [System.Convert]::FromBase64String("${{ secrets.SIGN_CERTIFICATE_BASE64 }}")
          $pfxPath   = Join-Path $env:RUNNER_TEMP "signing.pfx"
          [IO.File]::WriteAllBytes($pfxPath, $certBytes)
          # 後のステップから参照できるよう環境変数に保存
          "PFX_PATH=$pfxPath" | Out-File -FilePath $env:GITHUB_ENV -Append

      # ───────────────────────────────────────────
      # 6. signtool で MSIX / msixbundle に署名
      # ───────────────────────────────────────────
      - name: Sign MSIX with signtool
        shell: pwsh
        run: |
          # Windows SDK の signtool.exe を探す（複数バージョン対応）
          $signtool = Get-ChildItem `
            "C:\Program Files (x86)\Windows Kits\10\bin" `
            -Recurse -Filter signtool.exe |
            Sort-Object FullName -Descending |
            Select-Object -First 1 -ExpandProperty FullName

          if (-not $signtool) {
            throw "signtool.exe が見つかりません。Windows SDK がインストールされているか確認してください。"
          }

          Write-Host "signtool: $signtool"

          # 署名対象ファイルを収集（.msixbundle があれば優先、なければ .msix）
          $packages = Get-ChildItem "${{ env.APP_PACKAGES_DIR }}" `
            -Recurse -Include "*.msixbundle","*.msix" |
            Where-Object { $_.Name -notmatch "_Test" }   # テスト証明書付きを除外

          if ($packages.Count -eq 0) {
            throw "署名対象のパッケージが見つかりません: ${{ env.APP_PACKAGES_DIR }}"
          }

          New-Item -ItemType Directory -Force -Path "${{ env.SIGNED_OUTPUT_DIR }}" | Out-Null

          foreach ($pkg in $packages) {
            Write-Host "Signing: $($pkg.FullName)"

            & $signtool sign `
              /fd SHA256 `
              /td SHA256 `
              /tr http://timestamp.digicert.com `
              /f "$env:PFX_PATH" `
              /p "${{ secrets.SIGN_CERTIFICATE_PASSWORD }}" `
              "$($pkg.FullName)"

            if ($LASTEXITCODE -ne 0) {
              throw "署名に失敗しました: $($pkg.FullName) (exit code: $LASTEXITCODE)"
            }

            # 署名済みファイルを出力ディレクトリにコピー
            Copy-Item $pkg.FullName "${{ env.SIGNED_OUTPUT_DIR }}\" -Force
          }

      # ───────────────────────────────────────────
      # 7. 署名検証（オプションだが強く推奨）
      # ───────────────────────────────────────────
      - name: Verify signature
        shell: pwsh
        run: |
          $signtool = Get-ChildItem `
            "C:\Program Files (x86)\Windows Kits\10\bin" `
            -Recurse -Filter signtool.exe |
            Sort-Object FullName -Descending |
            Select-Object -First 1 -ExpandProperty FullName

          Get-ChildItem "${{ env.SIGNED_OUTPUT_DIR }}" | ForEach-Object {
            Write-Host "Verifying: $($_.FullName)"
            & $signtool verify /pa /v "$($_.FullName)"
            if ($LASTEXITCODE -ne 0) {
              throw "署名検証に失敗しました: $($_.FullName)"
            }
          }

      # ───────────────────────────────────────────
      # 8. 一時 PFX を削除（必須）
      # ───────────────────────────────────────────
      - name: Remove temporary PFX
        if: always()       # 署名ステップが失敗してもクリーンアップを実行
        shell: pwsh
        run: |
          if (Test-Path "$env:PFX_PATH") {
            Remove-Item "$env:PFX_PATH" -Force
            Write-Host "PFX ファイルを削除しました"
          }

      # ───────────────────────────────────────────
      # 9. GitHub Release を作成してアセットを添付
      # ───────────────────────────────────────────
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ github.ref_name }}
          name: Release ${{ github.ref_name }}
          draft: false
          prerelease: ${{ contains(github.ref_name, '-') }}  # v1.0.0-beta は pre-release
          generate_release_notes: true      # 前タグからのコミットを自動まとめ
          files: |
            ${{ env.SIGNED_OUTPUT_DIR }}/*.msixbundle
            ${{ env.SIGNED_OUTPUT_DIR }}/*.msix
```

---

## 5. 各ステップの詳細解説

### 5-1. `AppxPackageSigningEnabled=false` にする理由

MSBuild の wapproj は `/p:AppxPackageSigningEnabled=true`（デフォルト）の場合、ビルド時に自動署名しようとする。CI 環境では証明書ストアが空なのでエラーになる。そのため **ビルド時の署名を無効化し、後工程で `signtool` を明示的に呼ぶ** のが定石。

### 5-2. タイムスタンプサーバー

`/tr http://timestamp.digicert.com` は RFC 3161 タイムスタンプ。これを省略すると証明書の有効期限が切れた後にアプリが「署名が無効」と見なされる。他の信頼できる TSA：
- `http://timestamp.globalsign.com/scripts/timstamp.dll`
- `http://timestamp.sectigo.com`
- `http://tsa.starfieldtech.com`

### 5-3. `UapAppxPackageBuildMode=StoreUpload` vs `SideloadOnly`

| 値 | 用途 |
|----|------|
| `StoreUpload` | Store 提出用 `.msixupload` + `.msixbundle` を生成 |
| `SideloadOnly` | サイドロード配布用 `.msixbundle` のみ |
| `CI` | テスト用（.NET 6+ で追加） |

GitHub Release での直接配布なら `SideloadOnly` でも可。Store 提出を兼ねるなら `StoreUpload`。

### 5-4. バージョン番号の自動設定

`github.ref_name` は `v1.2.3` の形式なので、先頭の `v` を除いて `1.2.3.0`（4 桁）に変換して `/p:Version` に渡している。`Package.appxmanifest` の `Version` 属性が 4 桁必須なため。

---

## 6. 自己署名証明書の作成（開発・テスト用）

本番では商用 EV 証明書を使うこと。開発段階では PowerShell で自己署名証明書を生成できる。

```powershell
# 証明書を生成（Publisher は appxmanifest の Identity Publisher と一致させる）
$cert = New-SelfSignedCertificate `
  -Type Custom `
  -Subject "CN=MyPublisher" `
  -KeyUsage DigitalSignature `
  -FriendlyName "My WPF App Signing Cert" `
  -CertStoreLocation "Cert:\CurrentUser\My" `
  -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

# PFX としてエクスポート
$pwd = ConvertTo-SecureString -String "YourPassword" -Force -AsPlainText
Export-PfxCertificate `
  -Cert "Cert:\CurrentUser\My\$($cert.Thumbprint)" `
  -FilePath "MyCert.pfx" `
  -Password $pwd
```

---

## 7. よくあるエラーと対処

| エラー | 原因 | 対処 |
|--------|------|------|
| `signtool error: No certificates were found that met all the given criteria` | PFX パスワード不一致、または証明書の Subject が `appxmanifest` の Publisher と不一致 | PFX を再確認。`certutil -dump MyCert.pfx` で Subject を確認 |
| `Error APPX1201: The certificate used for package signing was not found` | `AppxPackageSigningEnabled=true` でビルドしたが証明書ストアに証明書がない | `AppxPackageSigningEnabled=false` にする |
| `APPX signing failed. SignTool reported an error: A certificate chain could not be built` | タイムスタンプサーバーに到達できない（ネットワーク制限） | タイムスタンプサーバーの URL を変更するか `/t` フラグを一時的に省略 |
| `The package couldn't be installed because a different package with the same name is already installed` | バージョン番号が同じ | タグ / バージョン番号を上げる |
| `Release assets: No files found` | `SIGNED_OUTPUT_DIR` が空 | 署名ステップのログで `Copy-Item` の成否を確認 |

---

## 8. Trusted People ストアへのインストール（サイドロード）

自己署名証明書を使う場合、インストール先マシンにも証明書を信頼させる必要がある。

```powershell
# 管理者 PowerShell で実行
Import-PfxCertificate `
  -FilePath "MyCert.pfx" `
  -CertStoreLocation "Cert:\LocalMachine\TrustedPeople" `
  -Password (ConvertTo-SecureString "YourPassword" -Force -AsPlainText)
```

商用証明書（DigiCert / Sectigo など）の場合は不要（Windows が既に信頼している）。

---

## 9. まとめ — チェックリスト

- [ ] PFX を Base64 変換し `SIGN_CERTIFICATE_BASE64` Secret に登録
- [ ] PFX パスワードを `SIGN_CERTIFICATE_PASSWORD` Secret に登録
- [ ] `Package.appxmanifest` の `Identity Publisher` が PFX の Subject と一致していること
- [ ] `AppxPackageSigningEnabled=false` でビルド
- [ ] `signtool` に `/tr`（タイムスタンプ）と `/fd SHA256` を必ず指定
- [ ] `if: always()` で PFX の一時ファイルをクリーンアップ
- [ ] `permissions: contents: write` を job または workflow に付与
- [ ] `softprops/action-gh-release@v2` で Release 作成とアセット添付
