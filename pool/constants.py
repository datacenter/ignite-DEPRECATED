# globals
END = "end"
NAME = "name"
SCOPE = "scope"
ROLE = "role"
START = "start"
TYPE = "type"
BLOCKS = "blocks"

#Pool role
MGMT = "Mgmt"

ROLE_OPTIONS = ['', MGMT]

# pool types
INTEGER = "Integer"
IPV4 = "IPv4"
IPV6 = "IPv6"

POOL_TYPES = [INTEGER, IPV4, IPV6]

# pool scopes
FABRIC = "Fabric"
GLOBAL = "Global"

SCOPE_OPTIONS = [GLOBAL, FABRIC]

# errors
ERR_INV_POOL_RANGE = "Invalid pool range"
ERR_MISMATCH_PREFIX_LEN = "Mismatch in prefix length"
ERR_POOL_FULL = "Pool is full"
ERR_POOL_IN_USE = "Pool is in use"
ERR_NON_FABRIC_POOL = "Fabric pool cannot be used for non fabric switch"
ERR_POOL_RANGE_OVERLAP = "Overlapping pool ranges"
ERR_MISMATCH_PREFIX_LEN_BLOCKS = "Network address differ across blocks"
ERR_ROLE_NOT_DEFINED = "Role not defined for pool"
ERR_MGMT_POOL_NOT_FOUND = "No Mgmt IP pool defined"
