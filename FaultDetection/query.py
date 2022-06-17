import argparse
import json
import csv
import sys 
import os.path
import git 

# Setup path to search for custom modules at the git root level
repo = git.Repo('.', search_parent_directories=True)
repo_root_path = repo.working_tree_dir
sys.path.insert(1, repo_root_path)

from SmartGridOntology import SmartGrid_Query as query

parser = argparse.ArgumentParser(description = "Convert turtle files for fault detection")
parser.add_argument('--infile', help="The filename of the ontology to convert", required=True)

def main():
    args = parser.parse_args()
    
    onto_filename = args.infile

    # import the graph query
    graph = query.SmartGridGraph(onto_filename)

    # You must query buses first
    graph.query_buses()
    # You must query double buses/connections after querying the buses
    graph.query_double_buses()
    # Before querying any further you need to query the generator after
    graph.query_generator()

    graph.query_nodes()

    controllers = [str(controller) for controller in graph.query_controllers()]
    for controller in controllers:
        print(controller)
    sensors = graph.query_sensors()
    for sensor in sensors:
        print(sensor)

       

if __name__ == "__main__":
    main()
