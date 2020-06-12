available_options = {'a', 'A', 'p', 'P', 'i', 'I', 'd', 'r', 'R'}

available_options_labels = {
    'a' : "append text",
    'A' : "append incremented numeric value",
    'p' : "prepend text",
    'P' : "prepend incremented numeric value",
    "i" : "insert text",
    "I" : "insert incremented numeric value",
    "d" : "delete text",
    "r" : "replace characters with text",
    "R" : "replace characters with incremented numeric value"
}

status_messages = [
    "Success",
    "Some items could not be renamed due to insufficient string size",
    "Duplicate items would result from renaming"
]

simulation_limit = 5 #number of files for which the renaming would be simulated
