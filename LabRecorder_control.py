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

"""""

file structure:
-data
--patient
---session (in our case part)
----run (in case one part is divided into many time segments)
"""""

import socket


s = socket.create_connection(("localhost", 22345))
s.sendall(b"select all\n")
#TODO: filename template
#s.sendall(b"filename {root:C:\\Data\\} {template:exp%n\\%p_block_%b.xdf} {run:1} {participant:P003} {task:MemoryGuided} {modality:eeg}\n")
# s.sendall(b"start\n")

#s.sendall(b"filename {template:%p/%s/%r.xdf} {run:1} {participant:w_w_15} {session:1} {task:Default} {modality:eeg}\n")

participant = "w_w_15"
session = 1
run = 1 
param_str = f"{{run:{run}}} {{participant:{participant}}} {{session:{session}}} {{task:Default}} {{modality:eeg}}\n"

print(param_str)
send_msg = b"filename {template:%p/%s/LabRecorder/%r.xdf} " + param_str.encode()
s.sendall(send_msg)

#do something
# s.sendall(b"stop\n")

# update runs or even sessions

# s.sendall(b"start\n")

