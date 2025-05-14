import json

class DefinitionError(Exception):
    """Custom exception for definition-related errors."""
    pass

class DefinitionManager:
    """Manages the definition dictionary for verbs and their properties."""
    
    def __init__(self):
        """Initialize the manager with an empty state."""
        self._definition_dict = {}
        self._action_functions = set()
        self._is_defining_verb = False
        self._is_defining_object = False
        self._actions_defined = False
        self._current_verb = None
        self._current_object = None

    def start_definition(self):
        """Initialize the definition dictionary."""
        self._definition_dict = {}
        self._action_functions = set()
        self._is_defining_verb = False
        self._is_defining_object = False
        self._actions_defined = False
        self._current_verb = None
        self._current_object = None
        return self

    def define_action_functions(self, list_of_action_functions):
        """Define the list of valid action functions."""
        if self._actions_defined:
            raise DefinitionError("Action functions can only be defined once after start_definition.")
        if self._is_defining_verb:
            raise DefinitionError("Cannot define action functions while defining a verb.")
        if not isinstance(list_of_action_functions, list):
            raise DefinitionError("Argument must be a list of action function names.")
        
        self._action_functions = set(list_of_action_functions)
        self._actions_defined = True

    def start_verb_definition(self, name, help_string, action_function):
        """Start defining a verb and add it to the definition dictionary."""
        if not self._actions_defined:
            raise DefinitionError("Must call define_action_functions before defining verbs.")
        if self._is_defining_verb:
            raise DefinitionError("Cannot nest start_verb_definition calls.")
        if not all(isinstance(arg, str) for arg in (name, help_string, action_function)):
            raise DefinitionError("All arguments must be strings.")
        if name in self._definition_dict:
            raise DefinitionError(f"Verb '{name}' is already defined.")
        if action_function not in self._action_functions:
            raise DefinitionError(f"Action function '{action_function}' is not in the defined list.")
        
        self._definition_dict[name] = {
            "name": name,
            "help": help_string,
            "action": action_function,
            "objects": {},
            "adjectives": {}
        }
        self._is_defining_verb = True
        self._current_verb = name

    def add_adverb(self, name, description):
        """Add an adverb to the current verb's adjectives dictionary."""
        if not self._is_defining_verb:
            raise DefinitionError("Can only add adverbs during an active verb definition.")
        if self._is_defining_object:
            raise DefinitionError("Cannot add adverbs while defining an object.")
        if not isinstance(name, str) or not isinstance(description, str):
            raise DefinitionError("Name and description must be strings.")
        
        current_adjectives = self._definition_dict[self._current_verb]["adjectives"]
        if name in current_adjectives:
            raise DefinitionError(f"Adverb '{name}' is already defined for verb '{self._current_verb}'.")
        
        current_adjectives[name] = {
            "name": name,
            "description": description
        }

    def define_object(self, name, description):
        """Define an object within the current verb's objects dictionary."""
        if not self._is_defining_verb:
            raise DefinitionError("Can only define objects during an active verb definition.")
        if self._is_defining_object:
            raise DefinitionError("Cannot nest define_object calls; call end_object_definition first.")
        if not isinstance(name, str) or not isinstance(description, str):
            raise DefinitionError("Name and description must be strings.")
        
        current_objects = self._definition_dict[self._current_verb]["objects"]
        if name in current_objects:
            raise DefinitionError(f"Object '{name}' is already defined for verb '{self._current_verb}'.")
        
        current_objects[name] = {
            "name": name,
            "description": description,
            "adjectives": {}
        }
        self._is_defining_object = True
        self._current_object = name

    def add_adjective(self, name, description):
        """Add an adjective to the current object's adjectives dictionary."""
        if not self._is_defining_object:
            raise DefinitionError("Can only add adjectives during an active object definition.")
        if not isinstance(name, str) or not isinstance(description, str):
            raise DefinitionError("Name and description must be strings.")
        
        current_objects = self._definition_dict[self._current_verb]["objects"]
        current_adjectives = current_objects[self._current_object]["adjectives"]
        if name in current_adjectives:
            raise DefinitionError(f"Adjective '{name}' is already defined for object '{self._current_object}'.")
        
        current_adjectives[name] = {
            "name": name,
            "description": description
        }

    def end_object_definition(self):
        """End the current object definition, validating and preparing for new objects."""
        if not self._is_defining_object:
            raise DefinitionError("No active object definition to end.")
        
        current_objects = self._definition_dict[self._current_verb]["objects"]
        object_entry = current_objects[self._current_object]
        required_fields = {"name", "description", "adjectives"}
        if not all(field in object_entry for field in required_fields):
            raise DefinitionError(f"Object '{self._current_object}' is missing required fields.")
        if not isinstance(object_entry["adjectives"], dict):
            raise DefinitionError(f"Object '{self._current_object}' has invalid adjectives structure.")
        
        self._is_defining_object = False
        self._current_object = None

    def end_verb_definition(self):
        """End the current verb definition, validating and preparing for new verbs."""
        if not self._is_defining_verb:
            raise DefinitionError("No active verb definition to end.")
        if self._is_defining_object:
            raise DefinitionError("Cannot end verb definition while an object definition is active.")
        
        verb_entry = self._definition_dict[self._current_verb]
        required_fields = {"name", "help", "action", "objects", "adjectives"}
        if not all(field in verb_entry for field in required_fields):
            raise DefinitionError(f"Verb '{self._current_verb}' is missing required fields.")
        if not isinstance(verb_entry["objects"], dict) or not isinstance(verb_entry["adjectives"], dict):
            raise DefinitionError(f"Verb '{self._current_verb}' has invalid objects or adjectives structure.")
        
        self._is_defining_verb = False
        self._current_verb = None

    def end_definition(self):
        """Finalize the definition process and return the dictionary as a JSON object."""
        if self._is_defining_verb:
            raise DefinitionError("Cannot end definition while a verb definition is active.")
        if self._is_defining_object:
            raise DefinitionError("Cannot end definition while an object definition is active.")
        if not self._actions_defined:
            raise DefinitionError("No action functions defined; definition is incomplete.")
        if not self._definition_dict:
            raise DefinitionError("Definition dictionary is empty; nothing to return.")
        
        for verb, entry in self._definition_dict.items():
            required_fields = {"name", "help", "action", "objects", "adjectives"}
            if not all(field in entry for field in required_fields):
                raise DefinitionError(f"Verb '{verb}' is missing required fields.")
            if not isinstance(entry["objects"], dict) or not isinstance(entry["adjectives"], dict):
                raise DefinitionError(f"Verb '{verb}' has invalid objects or adjectives structure.")
            if entry["action"] not in self._action_functions:
                raise DefinitionError(f"Verb '{verb}' uses an undefined action function.")
        
        return json.dumps(self._definition_dict, indent=2)


# Example usage
if __name__ == "__main__":
    manager = DefinitionManager()

    manager.start_definition()
    manager.define_action_functions(["do_action", "process_action"])

    manager.start_verb_definition("jump", "Makes the character jump.", "do_action")
    manager.add_adverb("quickly", "Jump in a fast manner.")
    manager.define_object("ledge", "A narrow edge to jump from.")
    manager.add_adjective("steep", "A sharply inclined ledge.")
    manager.end_object_definition()
    manager.end_verb_definition()

    manager.start_verb_definition("run", "Makes the character run.", "process_action")
    manager.add_adverb("slowly", "Run at a reduced pace.")
    manager.define_object("path", "A trail to run on.")
    manager.add_adjective("winding", "A path with many turns.")
    manager.end_object_definition()
    manager.end_verb_definition()

    result = manager.end_definition()
    print(result)