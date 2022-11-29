import json
import requests
from collections import defaultdict

################################################################################
#
# Look into an epochs block production slot gaps:
# - count SlotDeltas for variation graphs
# - look for specific max slot deltas (separated for slots shortly after epoch boundary and all other slots)
#
################################################################################

epoch_start=376
epochs=1

epoch_boundary_slots = 300    # define what we should count as "close to epoch boundary" (set to 0 if you want to ignore)

print_closeSlots = True    # specifically show very close filled slots 
print_deltaSlots = True     # show the summary of counted slot gaps
print_maxSlots = True      # show largest slot gap for this epoch

################################################################################

url = 'https://api.koios.rest/api/v0/blocks'

for epoch in range(epoch_start, epoch_start+epochs):
    prevSlot=0
    offset=0
    closeSlotCnt=0
    
    # Koios query filters
    params = dict(
        epoch_no='eq.%s' % str(epoch),
        select='abs_slot,epoch_slot,block_height,block_time,tx_count, block_size',
        order='abs_slot.asc',
    )

    slotStats = defaultdict(lambda: 0)
    slotDeltaMaxBoundary = 0
    slotDeltaMaxEpoch = 0

    while True:
        params.update({"offset": offset})
        offset+=1000
        print("processing ep%s blocks %s ..." % (epoch, offset))
        try:
            response = requests.get(url=url, params=params)
            jsonResponse = response.json()
            if len(jsonResponse) == 0: break
            for block in jsonResponse:
                #print("eSlotNo:", block['epoch_slot'], "  absSlotNo:", block['abs_slot'], "  blockNo:", block['block_height'], " at ", block['block_time'], " delta: b", int(block['epoch_slot'])-prevSlot)
                prevSlotDelta = int(block['epoch_slot'])-prevSlot

                # find the largest slot gap for this epoch
                if int(block['epoch_slot']) > epoch_boundary_slots:
                    if slotDeltaMaxEpoch<prevSlotDelta:
                        slotDeltaMaxEpoch = prevSlotDelta
                else:
                    if slotDeltaMaxBoundary<prevSlotDelta:
                        slotDeltaMaxBoundary = prevSlotDelta

                # print out close filled slot# to look at them in the gantt
                if (prevSlotDelta == 1) and print_closeSlots:
                    closeSlotCnt+=1
                    print("close Slot ", closeSlotCnt, ": ", block['abs_slot']-1,"  size: ", block['block_size'])

                # sum up deltaslot lengths (throw everything above 119sec into one 120 category)
                if prevSlotDelta > 119:
                    slotStats[120]+=1
                else:
                    slotStats[prevSlotDelta]+=1
                
                prevSlot = int(block['epoch_slot'])

        except Exception as err:
            print(f'Houston, we have an error: {err}')

    if print_deltaSlots:
        print("~~~~~~~~ DeltaSlots variation for ep%s ~~~~~~~~~~~~" % (epoch))
        for x in range(1, 121):
            print("d%s: %s" % (str(x).zfill(3), slotStats[x]))

    if print_maxSlots:
        print("~~~~~~~~ max DeltaSlots for ep%s ~~~~~~~~~~~~" % (epoch))
        print("Boundary: %s   Epoch: %s" % (slotDeltaMaxBoundary, slotDeltaMaxEpoch))
