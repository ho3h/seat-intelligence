def prog(program):
  return vm_exec(program, 0, [])

def vm_exec(program, pc, stack):
  match program:
    case List/Nil:
      match stack:
        case List/Nil:
          return 0
        case List/Cons:
          return stack.head
    case List/Cons:
      (op, arg) = program.head
      next_pc = pc + 1
      if op == 0:
        return vm_exec(program.tail, next_pc, List/Cons(arg, stack))
      else:
        if op == 1:
          return vm_binary(program.tail, next_pc, 1, stack)
        else:
          if op == 2:
            return vm_binary(program.tail, next_pc, 2, stack)
          else:
            if op == 3:
              return vm_dup(program.tail, next_pc, stack)
            else:
              if op == 4:
                return vm_swap(program.tail, next_pc, stack)
              else:
                if op == 5:
                  return vm_pop(program.tail, next_pc, stack)
                else:
                  if op == 6:
                    return vm_jz(program.tail, next_pc, arg, stack)
                  else:
                    return vm_binary(program.tail, next_pc, 7, stack)

def vm_binary(program, pc, op, stack):
  match stack:
    case List/Nil:
      return 0
    case List/Cons:
      rest_stack = stack.tail
      match rest_stack:
        case List/Nil:
          return 0
        case List/Cons:
          value = vm_calc(op, rest_stack.head, stack.head)
          return vm_exec(program, pc, List/Cons(value, rest_stack.tail))

def vm_calc(op, a, b):
  if op == 1:
    return a + b
  else:
    if op == 2:
      return a * b
    else:
      return a - b

def vm_dup(program, pc, stack):
  match stack:
    case List/Nil:
      return 0
    case List/Cons:
      return vm_exec(program, pc, List/Cons(stack.head, stack))

def vm_swap(program, pc, stack):
  match stack:
    case List/Nil:
      return 0
    case List/Cons:
      rest_stack = stack.tail
      match rest_stack:
        case List/Nil:
          return 0
        case List/Cons:
          new_stack = List/Cons(rest_stack.head, List/Cons(stack.head, rest_stack.tail))
          return vm_exec(program, pc, new_stack)

def vm_pop(program, pc, stack):
  match stack:
    case List/Nil:
      return 0
    case List/Cons:
      return vm_exec(program, pc, stack.tail)

def vm_jz(program, pc, target, stack):
  match stack:
    case List/Nil:
      return 0
    case List/Cons:
      if stack.head == 0:
        distance = target - pc
        return vm_exec(vm_skip(program, distance), target, stack.tail)
      else:
        return vm_exec(program, pc, stack.tail)

def vm_skip(program, distance):
  switch distance:
    case 0:
      return program
    case _:
      match program:
        case List/Nil:
          return program
        case List/Cons:
          return vm_skip(program.tail, distance - 1)
