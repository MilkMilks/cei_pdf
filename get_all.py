import os
import tabula
import re


def extract_tables_from_pdf(pdf_path):
    # Read PDF and extract tables
    tables = tabula.read_pdf(pdf_path, pages='all',
                             multiple_tables=True, stream=True)

    # Get the year from the PDF file name
    year = os.path.basename(pdf_path).split('.')[0]

    # Create output folder if it doesn't exist
    output_folder = "./output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create the output TSV file
    tsv_path = os.path.join(output_folder, f"{year}_cei.tsv")
    with open(tsv_path, 'w', encoding='utf-8') as tsv_file:
        tsv_file.write(
            "company_name\tlocation\tcei_{0}\tcei_{1}\tforbes_1000\n".format(year, int(year)+1))

        # Iterate through each table and save as CSV
        for i, table in enumerate(tables, start=1):
            csv_path = os.path.join(output_folder, f"{year}_table_{i}.csv")
            table.to_csv(csv_path, index=False)
            print(f"Table {i} from {year} extracted and saved as {csv_path}")

            # Read the CSV file with 'utf-8' encoding
            with open(csv_path, 'r', encoding='utf-8') as file:
                csv_contents = file.read()

            # Apply regular expression pattern to extract information
            pattern = r'^(.*?),"([^"]+)",.*?,((?:\d+\.?\d*|),(?:\d+\.?\d*|),(?:\d+\.?\d*|),)'
            matches = re.findall(pattern, csv_contents, re.MULTILINE)

            # If matches found, write extracted information to the output TSV file
            if matches:
                for match in matches:
                    company_name = match[0].strip()
                    location = match[1].strip()
                    last_fields = match[2].rstrip(',').split(',')
                    cei_2016 = last_fields[0] if len(last_fields) >= 1 else ""
                    cei_2015 = last_fields[1] if len(last_fields) >= 2 else ""
                    forbes_rank = last_fields[2] if len(
                        last_fields) >= 3 else ""
                    tsv_file.write(
                        f"{company_name}\t{location}\t{cei_2016}\t{cei_2015}\t{forbes_rank}\n")
            else:
                # Write the entire table to the output TSV file
                table.to_csv(tsv_file, sep='\t', index=False)
                print(f"Entire table from {year} saved as {tsv_path}")

    print(f"Extracted information from {year} saved as {tsv_path}")

    # Remove individual CSV files
    for i in range(1, len(tables) + 1):
        csv_path = os.path.join(output_folder, f"{year}_table_{i}.csv")
        os.remove(csv_path)
        print(f"Removed {csv_path}")


pdfs_dir = './pdfs'
for file in os.listdir(pdfs_dir):
    if file.endswith(".pdf"):
        pdf_path = os.path.join(pdfs_dir, file)
        extract_tables_from_pdf(pdf_path)
