param (
    [Parameter(Mandatory = $true)]
    [string]$AppName,

    [Parameter(Mandatory = $true)]
    [string]$BitwardenProjectId
)
$Error.Clear()

# Import the Microsoft Entra PowerShell module
Import-Module Microsoft.Graph.Applications


# Check if the BWS_ACCESS_TOKEN environment variable is set, if not, prompt for it
if (!(Test-Path Env:BWS_ACCESS_TOKEN -ErrorAction SilentlyContinue)) {
    Write-Host "BWS_ACCESS_TOKEN environment variable is not set. Please enter your Bitwarden access token:"
    $accessToken = Read-Host -Prompt "Enter your Bitwarden access token"
    Set-Item -Path Env:BWS_ACCESS_TOKEN -Value "$accessToken" -Force
    Write-Host "BWS_ACCESS_TOKEN environment variable set."
}

$TenantId = Read-Host -Prompt "Enter your tenant ID"

# Connect to the tenant
Write-Host "Connecting to tenant $TenantId..."
Connect-MgGraph -TenantId $TenantId -Scopes "Application.ReadWrite.All" -NoWelcome

# Check if the application already exists
$existingApp = Get-MgApplication -Filter "displayName eq '$AppName'" -ErrorAction SilentlyContinue
if ($existingApp) {
    Write-Host "Application '$AppName' already exists with ID: $($existingApp.AppId)"
    Write-Host "Exiting script."
    exit 0
}

# Register the new application
Write-Host "Registering new application: $AppName..."
$app = New-MgApplication -DisplayName $AppName

# Assign the LicenseAssignment.Read.All application permission
Write-Host "Assigning application permission: LicenseAssignment.Read.All..."
$apiPermission = @{
    ResourceId = "00000003-0000-0000-c000-000000000000" # Microsoft Graph resource ID
    Id         = "e2f98668-2877-4f38-a2f4-8202e0717aa1"         # LicenseAssignment.Read.All permission ID
}
Update-MgApplication -ApplicationId $app.Id -RequiredResourceAccess @(@{
        ResourceAppId  = $apiPermission.ResourceId
        ResourceAccess = @(@{
                Id   = $apiPermission.Id
                Type = "Role"
            })
    })

# Generate an application secret
Write-Host "Generating application secret..."
$passwordCred = @{
    displayName = 'Created in PowerShell'
    endDateTime = (Get-Date).AddMonths(24)
}
$secret = Add-MgApplicationPassword -applicationId $app.Id -PasswordCredential $passwordCred 
$appSecretValue = $secret.SecretText


# Store the application ID and secret using Bitwarden CLI
Write-Host "Storing application credentials in Bitwarden..."
$appId = $app.AppId
# Have the tenantID first 5 digits in the names
$ShortenedTenantId = $TenantId.Substring(0, 5)
$bwIdName = "CLIENT_ID_$ShortenedTenantId"
$bwSecretName = "CLIENT_SECRET_$ShortenedTenantId"

# Check if the application ID and secret already exist in Bitwarden
$BWSecrets = .\bws.exe secret list $BitwardenProjectId  | ConvertFrom-Json
$existingIdSecret = $BWSecrets | Where-Object { $_.key -eq $bwIdName -and $_.projectId -eq $BitwardenProjectId }
$existingSecret = $BWSecrets | Where-Object { $_.key -eq $bwSecretName -and $_.projectId -eq $BitwardenProjectId }
if ($existingIdSecret) {
    Write-Host "Application ID secret '$bwIdName' already exists in Bitwarden. Updating value..."
    $bwIdExistingId = $existingIdSecret.id
    .\bws.exe secret edit $bwIdExistingId --value  $appId 
}
else {
    Write-Host "Creating new application ID secret '$bwIdName' in Bitwarden..."
    .\bws.exe secret create $bwIdName $appId $BitwardenProjectId 
}
if ($existingSecret) {
    Write-Host "Application secret '$bwSecretName' already exists in Bitwarden. Updating value..."
    $bwSecretExistingId = $existingSecret.id
    .\bws.exe secret edit $bwSecretExistingId --value $appSecretValue
}
else {
    Write-Host "Creating new application secret '$bwSecretName' in Bitwarden..."
    .\bws.exe secret create $bwSecretName $appSecretValue $BitwardenProjectId
}

Write-Host "Application registered and credentials stored successfully!"
Write-Host "App ID: $appId"
Write-Host "App Secret: $appSecretValue"
Write-Host "Secrets stored securely in Bitwarden as $bwIdName and $bwSecretName."

# Grant admin consent by popup of window directed to the url https://login.microsoftonline.com/{organization}/adminconsent?client_id={client-id}
$adminConsentUrl = "https://login.microsoftonline.com/$TenantId/adminconsent?client_id=$($app.AppId)"
Start-Process $adminConsentUrl
Write-Host "Please grant admin consent by following the link: $adminConsentUrl"