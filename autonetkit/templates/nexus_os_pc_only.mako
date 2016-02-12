% if node.vpc:                                                         
! 
feature lacp
feature vpc
vpc domain ${node.vpc.domain_id}
 peer-keepalive destination ${node.vpc.dest} source ${node.mgmt.ip} vrf management
% endif
## Physical Interfaces
% for interface in node.interfaces:
!
    % if interface.pc == True:
interface ${interface.id}
        % if interface.member_vpc != True:
  description ${interface.description}
        % endif
        % if interface.comment:
  ! ${interface.comment}
        % endif
    % endif
    % if interface.channel_group:
interface ${interface.id}
        % if interface.member_port_vpc != True:
  description ${interface.description}
        % endif
        % if interface.comment:
  ! ${interface.comment}
        % endif
  channel-group ${interface.channel_group}
  no shut
    % else:
        % if interface.vpc_member_id:
    vpc ${interface.vpc_member_id}
        % endif
        % if interface.virt_port_channel:
   vpc peer-link
        % endif
    % endif
% endfor
