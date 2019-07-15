import click
import pandas as pd
import glob
import csv
from .taxa_tree import NCBITaxaTree


@click.group()
def main():
    pass
	
@main.command('data-table')
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('out', type=click.File('w'))
def data_table(file_path, out):
    """Concanate all the CSV files into one combined file"""
    all_files = glob.glob(file_path + "/*.csv")
    concat_list = []
    
    for filename in all_files: 
        df = pd.read_csv(open(filename, 'r'))
        concat_list.append(df)

    annotated = pd.concat(concat_list, axis=0, ignore_index=True)
    annotated.to_csv(out)

	
@main.command('filter-microbes')
@click.argument('out', type=click.File('w'))
def filter_taxa(out):
    """Parse NCBI File to return the phyla classification of a species"""
    taxa_tree, sci_name = NCBITaxaTree.parse_files()
    taxonomy = {}
    for taxon in sci_name:
        taxon = taxon.strip()
        if taxa_tree.taxonomic_rank(taxon, default=None) != None:
            taxonomy[taxon] = taxa_tree.taxonomic_tree_species(taxon, default=None).values()
    col_names = ['taxonomic_id', 'species', 'genus', 'family', 'order', 'class', 'phylum']
    annotated = pd.DataFrame.from_dict(taxonomy, columns=col_names, orient='index')
    annotated.to_csv(out)
	
@main.command('annotate-taxa')
@click.option('--microbes', default=True, help='Whether limit to microbes i.e., Bacteria and Virus, only')
@click.argument('out', type=click.File('w'))
def annotate(microbes, out):
    """Parse NCBI File to return the rank for given scientific name"""
    taxa_tree, sci_name = NCBITaxaTree.parse_files()
    rank_file, tax_rank, rank = {}, list(), ''
    bacteria, viruses, fungi = {}, {}, {}
    for taxon in sci_name:
        taxon = taxon.strip()
        if microbes == False:        
            rank_file[taxon] = taxa_tree.rank_of_species(taxon).values()
        else:
            tax_rank, rank = taxa_tree.rank_microbes(taxon, default=None)
            rank_file[taxon] = tax_rank
            if rank != None:   
                if rank == 'Viruses':
                    viruses[taxon] = tax_rank
                elif rank == 'Bacteria':
                    bacteria[taxon] = tax_rank	
                elif rank == 'Fungi':
                    fungi[taxon] = tax_rank			
    col_names = ['scientific name', 'taxonomic_id', 'rank']
    annotated = pd.DataFrame.from_dict(rank_file, columns=col_names, orient='index')
    annotated.to_csv(out)
    annotated = pd.DataFrame.from_dict(viruses, columns=col_names, orient='index')
    annotated.to_csv("NCBI_Virus_rank.csv")
    annotated = pd.DataFrame.from_dict(bacteria, columns=col_names, orient='index')
    annotated.to_csv("NCBI_Bacteria_rank.csv")
    annotated = pd.DataFrame.from_dict(fungi, columns=col_names, orient='index')
    annotated.to_csv("NCBI_Fungi_rank.csv")
	

if __name__ == '__main__':
    main()
