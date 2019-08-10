# motex
A binary analysis framework

## Documentation
[Introduction](#Introduction) 
[Configuration](#Configuration)  
[Commands](#Commands)  
[Api](#Api)  
[Contributing](#Contributing) 

# Introduction
## System requirements
Motex requires python 3.6+.

# Commands
## cmd 
`$ motex [command] [config] args`

## load binary
```bash
$ motex load test.toml
```

## run script 
```bash
$ motex.tools load test.toml script.py
```

# Api
## Data Structure
```
motex_function  {
	address
	name
	basicblock_leaders
	function_edges
	callsites_list
	basicblock_edges
	instructions_list
}

motex_callsite  {
	address
	return_address
	target_resolved
	target_address
	target_type
	target_name
	function_address
	basicblock_leader
}

motex_instruction  {
	address
	function_address
	basicblock_address
	content
	content_str
}

motex_segment  {
	segment_type
	segment_offset
	segment_virtual_address
	segment_virtual_size
	segment_physical_address
	segment_physical_size
	segment_flags
	segment_sections
	segment_section_addrs
}

motex_section  {
	section_name
	section_type
	section_offset
	section_virtual_address
	section_size
	section_entry_size
	section_entropy
	section_segments
}

motex_symbol  {
	symbol_num
	symbol_index
	symbol_value
	symbol_size
	symbol_type
	symbol_bind
	symbol_visibility
	symbol_name
	symbol_import_export
	symbol_version
}

motex_relocation  {
	relocation_address
	relocation_type
	relocation_symbol_value
	relocation_symbol_name
	relocation_computed_plt_address
}
```

## Api Functions
#### Working with functions
```python
>>> for function in this.functions.all():
        ...  print str(function)
        ...
        <motex_function>
        <motex_function> 
        <motex_function> 
        <motex_function> 

>>> motex_function = this.functions.get(index)
```

#### Working with callsites
```python
>>> for callsite in this.callsites.all():
        ...  print str(callsite)
        ...
        <motex_callsite>
        <motex_callsite> 
        <motex_callsite> 
        <motex_callsite> 

>>> motex_callsite = this.callsites.get(index)
```

#### Working with segments
```python
>>> for segment in this.segments.all():
        ...  print str(segment)
        ...
        <motex_segment>
        <motex_segment> 
        <motex_segment> 
        <motex_segment> 

>>> motex_segment = this.segments.get(index):
```

#### Working with instructions
```python
>>> for instruction in this.instructions.all():
        ...  print str(instruction)
        ...
        <motex_instruction>
        <motex_instruction>
        <motex_instruction>
        <motex_instruction>

>>> motex_instruction = this.instructions.get(address):
```

#### Working with symbols
```python
>>> for symbol in this.symbols.all():
        ...  print str(symbol)
        ...
        <motex_symbol>
        <motex_symbol>
        <motex_symbol>
        <motex_symbol>

>>> motex_symbol = this.symbols.get(index):
```

#### Working with relocations
```python
>>> for relocation in this.relocations.all():
        ...  print str(relocation)
        ...
        <motex_relocation>
        <motex_relocation>
        <motex_relocation>
        <motex_relocation>

>>> motex_relocation = this.relocations.get(index)
```

#### Working with sections
```python
>>> for section in this.sections.all():
        ...  print str(section)
        ...
        <motex_section>
        <motex_section>
        <motex_section>
        <motex_section>

>>> motex_section = this.sections.get(index)
```

# Contributing
