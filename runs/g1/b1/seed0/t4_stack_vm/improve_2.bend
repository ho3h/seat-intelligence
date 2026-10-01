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
      switch op:
        case 0:
          return vm_exec(program.tail, next_pc, List/Cons(arg, stack))
        case 1:
          return vm_binary(program.tail, next_pc, 1, stack)
        case 2:
          return vm_binary(program.tail, next_pc, 2, stack)
        case 3:
          match stack:
            case List/Nil:
              return 0
            case List/Cons:
              return vm_exec(program.tail, next_pc, List/Cons(stack.head, stack))
        case 4:
          match stack:
            case List/Nil:
              return 0
            case List/Cons:
              match stack.tail:
                case List/Nil:
                  return 0
                case List/Cons:
                  new_stack = List/Cons(stack.tail.head, List/Cons(stack.head, stack.tail.tail))
                  return vm_exec(program.tail, next_pc, new_stack)
        case 5:
          match stack:
            case List/Nil:
              return 0
            case List/Cons:
              return vm_exec(program.tail, next_pc, stack.tail)
        case 6:
          match stack:
            case List/Nil:
              return 0
            case List/Cons:
              if stack.head == 0:
                distance = arg - next_pc
                return vm_exec(vm_skip(program.tail, distance), arg, stack.tail)
              else:
                return vm_exec(program.tail, next_pc, stack.tail)
        case 7:
          return vm_binary(program.tail, next_pc, 7, stack)

def vm_binary(program, pc, op, stack):
  match stack:
    case List/Nil:
      return 0
    case List/Cons:
      match stack.tail:
        case List/Nil:
          return 0
        case List/Cons:
          if op == 1:
            value = stack.tail.head + stack.head
          else:
            if op == 2:
              value = stack.tail.head * stack.head
            else:
              value = stack.tail.head - stack.head
          return vm_exec(program, pc, List/Cons(value, stack.tail.tail))

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
