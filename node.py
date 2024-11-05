class Node:
    def __init__(self, id, name="", cores=0, memory=0, cores_available=0, memory_available=0, location=(float('inf'), float('inf')),
                 status=1, nrt=None, parallel_f=None, sequential_f=None):
        self.id = id
        self.name = name
        self.status = status
        self.cores = cores
        self.memory = memory
        self.cores_available = cores_available
        self.memory_available = memory_available
        self.location = location
        self.parallel_f = parallel_f
        self.sequential_f = sequential_f
        self.nrt=nrt

    def set_status(self, status):
        self.status = status

    def set_cores_available(self, cores):
        self.cores_available = cores
        self.update_status()

    def set_memory_available(self, memory):
        self.memory_available = memory

    def update_available_cores(self, new_cores):
        self.cores_available = self.cores_available + new_cores
        self.update_status()

    # status = 1 underloaded, else, not underloaded
    def update_status(self):
        if self.cores_available > 0.2*self.cores:
            self.status = 1
        else:
            self.status = 0

    def initialization(self):
        self.set_cores_available(self.cores)
        self.set_memory_available(self.memory)
        self.set_status(1)

    # Note Closed
