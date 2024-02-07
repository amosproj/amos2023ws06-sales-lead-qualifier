# Automatic SBOM generation

```console
pipenv install
pipenv shell

pip install pipreqs
pip install cyclonedx-bom
pip install pip-licenses

# Create the SBOM (cyclonedx-bom) based on (pipreqs) requirements that are actually imported in the .py files

$sbom = pipreqs --print | cyclonedx-py -r -pb -o - -i -

# Create an XmlDocument object
$xml = New-Object System.Xml.XmlDocument

# Load XML content into the XmlDocument
$xml.LoadXml($sbom)


# Create an empty CSV file
$csvPath = "SBOM.csv"

# Initialize an empty array to store rows
$result = @()

# Iterate through the XML nodes and create rows for each node
$xml.SelectNodes("//*[local-name()='component']") | ForEach-Object {

    $row = @{
        "Version" = $_.Version
        "Context" = $_.Purl
        "Name" = if ($_.Name -eq 'scikit_learn') { 'scikit-learn' } else { $_.Name }
    }

    # Get license information
    $match = pip-licenses --from=mixed --format=csv --with-system --packages $row.Name | ConvertFrom-Csv

    # Add license information to the row
    $result += [PSCustomObject]@{
        "Context" = $row.Context
        "Name" = $row.Name
        "Version" = $row.Version
        "License" = $match.License
    }
}

# Export the data to the CSV file
$result | Export-Csv -Path $csvPath -NoTypeInformation

# Create the license file
$licensePath = $csvPath + '.license'
@"
SPDX-License-Identifier: CC-BY-4.0
SPDX-FileCopyrightText: 2023 Fabian-Paul Utech <f.utech@gmx.net>
"@ | Out-File -FilePath $licensePath

exit

```
