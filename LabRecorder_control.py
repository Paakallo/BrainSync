"""""
If you check the box to EnableRCS then LabRecorder exposes some rudimentary controls via TCP socket.

Currently supported commands include:

select all
select none
start
stop
update
filename ...
filename is followed by a series of space-delimited options enclosed in curly braces. e.g. {root:C:\root_data_dir}

root - Sets the root data directory.
template - sets the File Name / Template. Will unselect BIDS option. May contain wildcards.
task - will replace %b in template
run - will replace %n in template (not working?)
participant - will replace %p in template
session - will replace %s in template
acquisition - will replace %a in template
modality - will replace %m in template. suggested values: eeg, ieeg, meg, beh

"""""

import socket


s = socket.create_connection(("localhost", 22345))
s.sendall(b"select all\n")
s.sendall(b"filename {root:C:\\Data\\} {template:exp%n\\%p_block_%b.xdf} {run:2} {participant:P003} {task:MemoryGuided}\n")
# s.sendall(b"start\n")