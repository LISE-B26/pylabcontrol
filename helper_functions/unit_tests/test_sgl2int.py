import helper_functions.sgl2int as s2i
import numpy as np


# = test 1
U32_start = np.random.randint(0,2.0**16) * np.random.randint(0,2.0**16)
print('random 32 bit integer {:d}'.format(U32_start))

SGL = s2i.U32_to_SGL(U32_start)

print('converted float {:e}'.format(SGL))

U32 = s2i.SGL_to_U32(SGL)
print('back converted random 32 bit integer {:d}'.format(U32))

if (U32_start - U32) / (U32_start + U32)  == 0:
    print('== Test 1 passed ==')
else:
     print('TEST 1 FAILED')




# = test 2
SGL_start = np.random.random()
print('random float {:e}'.format(SGL_start))

U32 = s2i.SGL_to_U32(SGL_start)

print('converted random 32 bit integer {:d}'.format(U32))


SGL = s2i.U32_to_SGL(U32)
print('back converted float {:e}'.format(SGL))

if (SGL_start - SGL) / (SGL_start + SGL)  <1e-7:
    print('== Test 2 passed ==')
else:
     print('TEST 2 FAILED')




