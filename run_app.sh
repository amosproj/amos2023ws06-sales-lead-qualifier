# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

#!/bin/bash

application_name="sumup_app"

# Start building the docker command
command="docker run -i"

# Read each line in the file
while IFS= read -r line; do
    echo $line
    # Skip lines that start with '#' or are empty
    if [[ $line =~ ^# ]] || [[ -z $line ]]; then
        continue
    fi

    # Append non-comment lines to the command
    command+=" -e $line"
done < ".env"

command+=" $application_name"

# Run the command
echo "Running command: $command"
eval $command
