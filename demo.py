"""Two finite-resource autonomy examples; Python 3.10+, standard library only.

This is a deterministic state-based planning demonstrator, not a trained AI,
flight controller, or measured hardware benchmark. All numerical inputs are
illustrative. Run: python demo.py --output results.json
"""
import argparse
import heapq
import json
import math
from dataclasses import dataclass, field

@dataclass
class Ledger:
    energy_wh: float
    reserve_wh: float
    revision: int = 0
    records: list = field(default_factory=list)

    def event(self, kind, **details):
        self.records.append(dict(kind=kind, revision=self.revision, **details))

    def update(self, **details):
        self.revision += 1
        self.event('OBSERVATION_UPDATE', **details)

    def execute(self, name, task_wh, overhead_wh, revision, valid=True):
        # In this synchronous example, validation and commit share a revision.
        cost = task_wh + overhead_wh
        allow = valid and revision == self.revision and self.energy_wh-cost >= self.reserve_wh
        self.event('COMMIT' if allow else 'DENY', action=name,
                   task_wh=task_wh, overhead_wh=overhead_wh,
                   before_wh=self.energy_wh,
                   after_wh=self.energy_wh-cost if allow else self.energy_wh,
                   valid=valid, proposed_revision=revision)
        if allow:
            self.energy_wh -= cost
        return allow

def route(start, goal, blocked, width=5, height=5):
    """A* builds a route from the current map, without prewritten routes."""
    dist={start: 0}; parent={}; queue=[(0, 0, start)]
    while queue:
        _, cost, p=heapq.heappop(queue)
        if cost != dist[p]:
            continue
        if p == goal:
            path=[p]
            while p != start:
                p=parent[p]; path.append(p)
            return list(reversed(path))
        for dx,dy in [(1,0),(0,1),(-1,0),(0,-1)]:
            n=(p[0]+dx,p[1]+dy)
            if not (0 <= n[0] < width and 0 <= n[1] < height) or n in blocked:
                continue
            nc=cost+1
            if nc < dist.get(n, math.inf):
                dist[n]=nc; parent[n]=p
                h=abs(goal[0]-n[0])+abs(goal[1]-n[1])
                heapq.heappush(queue,(nc+h,nc,n))
    return None

def recovery_plan(available, energy, reserve):
    """Dijkstra composes equipment primitives from current availability.

    State = (active backup sensor, valid attitude estimate, stabilized).
    Only a declared equipment model is used; no list of fault-response pairs.
    """
    initial=('',False,False)
    queue=[(0.0,initial,[])];best={initial:0.0}
    while queue:
        cost,state,plan=heapq.heappop(queue)
        if cost != best[state]:
            continue
        active,valid,stable=state
        if stable:
            return plan
        choices=[]
        for name,start_cost in [('B',2.0),('C',4.0)]:
            if available.get(name,False) and active != name:
                choices.append(('activate_'+name,start_cost,(name,False,False)))
        if active and available.get(active,False) and not valid:
            choices.append(('verify_'+active,1.0,(active,True,False)))
        if valid and not stable:
            choices.append(('stabilize',3.0,(active,True,True)))
        for name,task_cost,next_state in choices:
            nc=cost+task_cost+0.5
            if energy-nc < reserve:
                continue
            if nc < best.get(next_state,math.inf):
                best[next_state]=nc
                step=dict(action=name,task_wh=task_cost,overhead_wh=0.5,
                          before_state=state,after_state=next_state)
                heapq.heappush(queue,(nc,next_state,plan+[step]))
    return None

def spacecraft_case(available):
    led=Ledger(30.0,10.0)
    old_revision=led.revision
    led.event('PROPOSE',action='science_with_primary_A')
    led.update(primary_A='failed',communication='unavailable',backup_availability=available,
               fault_owner='attitude_sensor_A')
    old_ok=led.execute('science_with_primary_A',2.0,0.5,old_revision,False)
    plan=recovery_plan(available,led.energy_wh,led.reserve_wh)
    state=('',False,False)
    if plan is None:
        led.event('OPEN',reason='no_model_feasible_recovery_plan')
    else:
        for step in plan:
            led.event('PROPOSE',**step)
            ok=led.execute(step['action'],step['task_wh'],step['overhead_wh'],
                           led.revision,state==step['before_state'])
            if not ok:
                break
            state=step['after_state']
    scan_ok=led.execute('optional_science_scan',15.0,0.5,led.revision,state[2])
    # This only charges one essential control interval. No attitude dynamics,
    # drift, thrust, or continuing survival are implied when a plan is OPEN.
    control_ok=led.execute('essential_control_one_interval',0.2,0.0,led.revision)
    self_state=dict(owned_equipment=['sensor_A','sensor_B','sensor_C','attitude_controller'],
                    unavailable_equipment=['sensor_A']+[f'sensor_{n}' for n in available if not available[n]],
                    remaining_energy_wh=round(led.energy_wh,6),reserve_wh=led.reserve_wh,
                    pending_task='optional_science_scan',
                    unresolved=['physical_attitude_dynamics','long_term_survival'],
                    attitude_estimate_valid=state[1],symbolic_stabilization=state[2],
                    evidence_revision=led.revision)
    led.event('SELF_STATE',**self_state)
    return dict(primary_sensor='failed',communication='unavailable',available=available,
                old_command_accepted=old_ok,plan=plan,
                recovery_status='model_stabilized' if state[2] else 'OPEN',
                optional_scan_accepted=scan_ok,essential_control_accepted=control_ok,
                final_energy_wh=round(led.energy_wh,6),reserve_wh=led.reserve_wh,
                self_state=self_state,ledger=led.records)

def nasa_example():
    return dict(example='interstellar_spacecraft_equipment_failure_and_link_loss',
                inputs='illustrative',
                scope='symbolic equipment planning and energy accounting; no spacecraft attitude dynamics',
                backup_B=spacecraft_case({'B':True,'C':True}),
                backup_C=spacecraft_case({'B':False,'C':True}),
                no_backup=spacecraft_case({'B':False,'C':False}))

def driving_case(initial_energy):
    led=Ledger(initial_energy,4.0)
    start=(0,2);destination=(4,2);blocked=set()
    initial=route(start,destination,blocked)
    old_revision=led.revision
    led.event('PROPOSE',route=initial,task_wh=4.0,overhead_wh=0.5)
    # Connectivity loss does not itself invalidate onboard perception.
    # A concurrent, independently sensed road closure invalidates the route.
    blocked.add((2,2))
    led.update(network='unavailable',blocked_cell=(2,2),onboard_perception='valid')
    old_accepted=led.execute('stale_route',4.0,0.5,old_revision,False)
    revised=route(start,destination,blocked)
    steps=len(revised)-1
    led.event('PROPOSE',route=revised,terminal='destination',task_wh=float(steps),overhead_wh=0.5)
    dest_ok=led.execute('offline_destination_route',float(steps),0.5,led.revision,True)
    selected=destination;selected_route=revised
    if not dest_ok:
        # Candidate refuges are inputs; the selected route is computed online.
        candidates=[]
        for refuge in [(1,1),(3,1)]:
            path=route(start,refuge,blocked)
            if path:
                cost=float(len(path)-1)+0.5
                if led.energy_wh-cost >= led.reserve_wh:
                    candidates.append((cost,refuge,path))
        if candidates:
            cost,selected,selected_route=min(candidates)
            led.event('PROPOSE',route=selected_route,terminal='refuge',task_wh=cost-0.5,overhead_wh=0.5)
            accepted=led.execute('offline_refuge_route',cost-0.5,0.5,led.revision,True)
        else:
            selected=None;selected_route=None;accepted=False
            led.event('OPEN',reason='no_model_certified_terminal_route')
    else:
        accepted=True
    control_ok=led.execute('essential_control_one_interval',0.2,0.0,led.revision)
    self_state=dict(owned_equipment=['onboard_perception','onboard_planner','vehicle_controller'],
                    unavailable_services=['network'],onboard_perception='valid_in_grid_model',
                    remaining_energy_wh=round(led.energy_wh,6),reserve_wh=led.reserve_wh,
                    selected_terminal='destination' if dest_ok else ('refuge' if selected else 'OPEN'),
                    unresolved=['lane_and_braking_dynamics','continuous_collision_avoidance'],
                    evidence_revision=led.revision)
    led.event('SELF_STATE',**self_state)
    return dict(initial_energy_wh=initial_energy,network='unavailable',
                old_route_accepted=old_accepted,destination_route_accepted=dest_ok,
                selected_terminal='destination' if dest_ok else ('refuge' if selected else 'OPEN'),
                selected_cell=selected,selected_route=selected_route,
                selected_route_accepted=accepted,essential_control_accepted=control_ok,
                final_energy_wh=round(led.energy_wh,6),reserve_wh=led.reserve_wh,
                self_state=self_state,ledger=led.records)

def driving_example():
    return dict(example='network_disconnected_autonomous_vehicle',inputs='illustrative',
                scope='high-level grid route planning; no lane, speed, braking or collision dynamics',
                normal_budget=driving_case(20.0),limited_budget=driving_case(10.0))

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',default='results.json')
    args=p.parse_args()
    data={'version':'0.1','date':'2026-10-13',
          'method':'deterministic state-based planner with resource gate and provenance ledger',
          'performance_claim':'illustrative execution only; not a measured AI or hardware advantage',
          'nasa':nasa_example(),'driving':driving_example()}
    # Invariants cover actual outputs, including denial without battery credit.
    for case in [data['nasa']['backup_B'],data['nasa']['backup_C'],data['nasa']['no_backup'],
                 data['driving']['normal_budget'],data['driving']['limited_budget']]:
        for event in case['ledger']:
            if event['kind']=='COMMIT':
                assert event['after_wh'] >= case['reserve_wh']
                assert abs(event['before_wh']-event['after_wh']-
                           event['task_wh']-event['overhead_wh']) < 1e-9
            if event['kind']=='DENY':
                assert event['before_wh']==event['after_wh']
    assert not data['nasa']['backup_B']['old_command_accepted']
    assert data['nasa']['backup_B']['recovery_status']=='model_stabilized'
    assert data['nasa']['backup_C']['plan'][0]['action']=='activate_C'
    assert data['nasa']['no_backup']['recovery_status']=='OPEN'
    assert not data['nasa']['backup_B']['optional_scan_accepted']
    assert data['driving']['normal_budget']['selected_terminal']=='destination'
    assert data['driving']['limited_budget']['selected_terminal']=='refuge'
    with open(args.output,'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
    print(json.dumps({'nasa_B_final_wh':data['nasa']['backup_B']['final_energy_wh'],
                      'nasa_C_final_wh':data['nasa']['backup_C']['final_energy_wh'],
                      'driving_normal_wh':data['driving']['normal_budget']['final_energy_wh'],
                      'driving_limited_wh':data['driving']['limited_budget']['final_energy_wh'],
                      'invariants':'passed','output':args.output},ensure_ascii=False))

if __name__=='__main__':
    main()
