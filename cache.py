import matplotlib.pyplot as plt
import numpy as np
import math
class Cache:
    def __init__(self, cache_size, block_size, associativity, replacement_policy):
        self.cache_size = cache_size
        self.block_size = block_size
        self.associativity = associativity
        self.num_lines = cache_size // block_size
        self.replacement_policy = replacement_policy
        self.cache_dm = {} 
        self.cache_fa = [None] * self.num_lines
        self.cache_sa = {}
        self.counter = 1  

    def simulate_dm_cache(self, file_name):
        hits = 0.0
        misses = 0.0
        self.counter  = 1

        with open(file_name, 'r') as file:
            self.counter = 1
            for line in file:
                n = len(line)
                self.counter += 1


                words = line.split()
                address = words[1]
                # print("address read in:",address)

                address_int = int(address, 16)
                if address_int == 0:
                    address_string = '0'  # Handle special case when address is 0
                    address_string = address_string.zfill(32)  # Assumes 32-bit addresses

                else:
                    address_string = format(address_int, 'b')
                    address_string = address_string.zfill(32)  

                
                # print("address string: ", address_string)

                # print("address converted to int:", address_int)
               
                set_size = int(math.log2(self.num_lines))
                # print("set size:",set_size)
                offset_size = int(math.log2(self.block_size))
                tag_size = int(len(address_string) - set_size - offset_size)

                # print(tag_size)
                set_bits = address_string[tag_size:tag_size + set_size]
                tag_bits = address_string[:tag_size]
                # print(set_bits)
                offset_bits = address_string[-offset_size:] 

                set_decimal = int(set_bits, 2)
                tag_decimal = int(tag_bits, 2)

                line_to_insert = CacheLine(set_decimal, tag_decimal, self.counter)
                

                if set_decimal not in self.cache_dm:
                    misses += 1
                    self.cache_dm[set_decimal] = [line_to_insert]  

                else:
                    current_line = self.cache_dm[set_decimal][0]  # Since it's direct-mapped, there will be only one line
                    if current_line.tag == line_to_insert.tag:
                        hits += 1
                        self.cache_dm[set_decimal][0] = line_to_insert

                    else:
                        self.cache_dm[set_decimal][0] = line_to_insert
                        misses += 1
            hit_rate = hits / (hits + misses)
            print("hit rate: ", hits / (hits + misses))
            return hit_rate
    def simulate_fa_cache(self, file_name):
        hits = 0.0
        misses = 0.0
        counter = 1
        self.counter = 1
        replacement_policy = self.replacement_policy 

        with open(file_name, 'r') as file:
            for line in file:
                n = len(line)
                counter += 1

                words = line.split()
                address = words[1]

                address_int = int(address, 16)
                if address_int == 0:
                    address_string = '0'
                    address_string = address_string.zfill(32)
                else:
                    address_string = format(address_int, 'b')
                    address_string = address_string.zfill(32)

                offset_size = int(math.log2(self.block_size))
                tag_size = int(len(address_string) - offset_size)

                tag_bits = address_string[:tag_size]
                offset_bits = address_string[-offset_size:]

                tag_decimal = int(tag_bits, 2)
                offset_decimal = int(offset_bits, 2)

                # Now create a cache line to add to the cache
                line_to_insert = CacheLine(0, tag_decimal, counter)

                found_hit = False
                for cache_line in self.cache_fa:
                    if cache_line is not None:
                        if cache_line.tag == line_to_insert.tag:
                            hits += 1
                            found_hit = True
                            # Update the counter for LRU replacement policy
                            if replacement_policy == 'lru':
                                cache_line.counter = counter
                            break

                if not found_hit:
                    misses += 1
                    # If there's a miss, do the replacement strategy
                    if replacement_policy == 'fifo':
                        index_to_replace = self.find_fifo_line(self.cache_fa)
                    elif replacement_policy == 'lru':
                        index_to_replace = self.find_lru_line(self.cache_fa)
                    self.cache_fa[index_to_replace] = line_to_insert
        hit_rate = hits / (hits + misses)
        print("hit rate: ", hits / (hits + misses))
        return hit_rate


    def find_lru_line(self, cache):
        min_counter = float('inf')
        index = 0

        for i in range(len(cache)):
            if cache[i] is None:
                return i
            elif cache[i].counter < min_counter:
                min_counter = cache[i].counter
                index = i

        return index
    def print_cache_sa(self):
        for set_index, cache_lines in self.cache_sa.items():
            print("Set Index:", set_index)
            for cache_line in cache_lines:
                print("Cache Line Tag:", cache_line.tag)
                print("Cache Line Counter:", cache_line.counter)

    def find_fifo_line(self, cache):
        index = 0

        for i in range(len(cache)):
            if cache[i] is None:
                return i
            elif cache[i].counter < cache[index].counter:
                index = i

        return index
    def get_empty_set(self):
        for i in range(len(self.cache_fa)):
            if self.cache_fa[i] is None:
                return True, i
        return False, 0
                
    def simulate_sa_cache(self, file_name):
        hits = 0.0
        misses = 0.0
        replacement_policy = self.replacement_policy

        with open(file_name, 'r') as file:
            self.counter = 1
            for line in file:
                self.counter += 1  
                n = len(line)

                words = line.split()
                address = words[1]
                # print("address read in:",address)

                address_int = int(address, 16)
                if address_int == 0:
                    address_string = '0'  # Handle special case when address is 0
                    address_string = address_string.zfill(32)  # 32-bit addresses

                else:
                    address_string = format(address_int, 'b')
                    address_string = address_string.zfill(32)  

                

                set_size = int(math.log2(self.num_lines // self.associativity))
                offset_size = int(math.log2(self.block_size))
                tag_size = int(len(address_string) - set_size - offset_size)

                set_bits = address_string[tag_size:tag_size + set_size]
                tag_bits = address_string[:tag_size]
                offset_bits = address_string[-offset_size:]
                set_decimal = int(set_bits, 2)
                tag_decimal = int(tag_bits, 2)

                # Check if the cache has this set occupied
                line_to_insert = CacheLine(set_decimal, tag_decimal, self.counter)
                # print('SET: ', set_decimal, "tag: ", tag_decimal)
                if set_decimal not in self.cache_sa:
                    # print("value not in cache yet")
                    self.cache_sa[set_decimal] = []  
                    misses += 1
                    self.cache_sa[set_decimal].append(line_to_insert)
                else: 
                    # now I am at a set in the cache where I have a list already
                    # go through the list and see if any of the cache lines are None or replaceable
                    replace_flag = False  # add a flag to track if replacement occurred
                    for cache_line_index in range(len(self.cache_sa[set_decimal])):
                        # print("SET: ", set_decimal, "current tag", self.cache_sa[set_decimal][cache_line_index].tag, "tag to insert", line_to_insert.tag, line_to_insert.counter)
                        if self.cache_sa[set_decimal][cache_line_index] is None:
                            misses += 1
                            self.cache_sa[set_decimal][cache_line_index] = line_to_insert  # replace None with line_to_insert
                            replace_flag = True  # set replace_flag to True
                            break  
                        elif self.cache_sa[set_decimal][cache_line_index].tag == line_to_insert.tag:
                            hits += 1
                            if replacement_policy == 'fifo':
                                index_to_replace = self.find_fifo_line(self.cache_sa[set_decimal])
                            elif replacement_policy == 'lru':
                                index_to_replace = self.find_lru_line(self.cache_sa[set_decimal])
                            self.cache_sa[set_decimal][index_to_replace] = line_to_insert
                            replace_flag = True  
                            break 

                    if not replace_flag:  
                        misses += 1
                        self.cache_sa[set_decimal].append(line_to_insert)

                # Calculate hit rate
            total_requests = hits + misses
            hit_rate = hits / total_requests 

            print("hit rate: ",hit_rate)
            return hit_rate

            
class CacheLine:
    def __init__(self, set, tag, counter):
        self.set = set
        self.tag = tag
        self.counter = counter


def create_caches():
    cache_sizes = [512, 1024, 2048, 4096, 8192, 16384]
    associativities = [1, -1, 2, 4, 8] 
    replacement_policies = ["fifo", "lru"] 
    caches = []
    for cache_size in cache_sizes:
        for associativity in associativities:
            if associativity >= 4:
                size = 64 // 4
            else:
                size = 64
            for replacement_policy in replacement_policies:
                if cache_size > 8000:
                    cache = Cache(cache_size, size, associativity, replacement_policy)
                else:    
                    cache = Cache(cache_size, size, associativity, replacement_policy)
                caches.append(cache)
    return caches
def get_hit_rates(caches, trace_file):
    cache_sizes = [cache.cache_size for cache in caches]
    hit_rates = {}
    for cache in caches:
        if cache.associativity == 1:
            # Direct Mapped Cache
            cache_design = "Direct Mapped"
            hit_rate = cache.simulate_dm_cache(trace_file)
            hit_rates.setdefault(cache_design, []).append(hit_rate)
        elif cache.associativity == -1 and cache.replacement_policy == "fifo":
            # Fully Associative Cache with FIFO replacement policy
            cache_design = "Fully Associative (FIFO)"
            hit_rate = cache.simulate_fa_cache(trace_file)
            hit_rates.setdefault(cache_design, []).append(hit_rate)
        elif cache.associativity == -1 and cache.replacement_policy == "lru":
            # Fully Associative Cache with LRU replacement policy
            cache_design = "Fully Associative (LRU)"
            hit_rate = cache.simulate_fa_cache(trace_file)
            hit_rates.setdefault(cache_design, []).append(hit_rate)
        elif cache.associativity > 1 and cache.replacement_policy == "fifo":
            # Set Associative Cache with FIFO replacement policy
            cache_design = f"{cache.associativity}-Way Set Associative (FIFO)"
            hit_rate = cache.simulate_sa_cache(trace_file)
            hit_rates.setdefault(cache_design, []).append(hit_rate)
        elif cache.associativity > 1 and cache.replacement_policy == "lru":
            cache_design = f"{cache.associativity}-Way Set Associative (LRU)"
            hit_rate = cache.simulate_sa_cache(trace_file)
            hit_rates.setdefault(cache_design, []).append(hit_rate)
    
    return hit_rates



def main():
    caches = create_caches()
    trace_file = "swim.trace"
    # cache_sizes = np.linspace(500, 24200, num  =12)

    hit_rates = get_hit_rates(caches, trace_file)

    for cache_design_key, hit_rate_values in hit_rates.items():
        if cache_design_key == "Direct Mapped":
            cache_sizes = np.linspace(500, 24200, num  =12)
            plt.plot(cache_sizes, hit_rate_values, label=cache_design_key)
        else:
            cache_sizes = np.linspace(500, 24200, num  =6)
            plt.plot(cache_sizes, hit_rate_values, label=cache_design_key)

    plt.xlabel('Cache Size (Bytes)')
    plt.ylabel('Hit Rate')
    plt.title('Cache Hit Rate for Different Cache Designs')
    plt.grid(True)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()

# MY NAME IS JORDAN GILLISPIE