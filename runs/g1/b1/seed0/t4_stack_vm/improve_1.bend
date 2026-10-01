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
      if op < 4:
        if op < 2:
          if op == 0:
            return vm_exec(program.tail, next_pc, List/Cons(arg, stack))
          else:
            return vm_binary(program.tail, next_pc, 1, stack)
        else:
          if op == 2:
            return vm_binary(program.tail, next_pc, 2, stack)
          else:
            match stack:
              case List/Nil:
                return 0
              case List/Cons:
                return vm_exec(program.tail, next_pc, List/Cons(stack.head, stack))
      else:
        if op < 6:
          if op == 4:
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
                    return vm_exec(program.tail, next_pc, new_stack)
          else:
            match stack:
              case List/Nil:
                return 0
              case List/Cons:
                return vm_exec(program.tail, next_pc, stack.tail)
        else:
          if op == 6:
            match stack:
              case List/Nil:
                return 0
              case List/Cons:
                if stack.head == 0:
                  distance = arg - next_pc
                  return vm_exec(vm_skip(program.tail, distance), arg, stack.tail)
                else:
                  return vm_exec(program.tail, next_pc, stack.tail)
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
          if op == 1:
            value = rest_stack.head + stack.head
          else:
            if op == 2:
              value = rest_stack.head * stack.head
            else:
              value = rest_stack.head - stack.head
          return vm_exec(program, pc, List/Cons(value, rest_stack.tail))

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
