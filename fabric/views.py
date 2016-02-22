from django.shortcuts import render

from rest_framework.response import Response

import services
from utils.baseview import BaseView
from serializers import *


class TopologyListView(BaseView):

    def get(self, request, format=None):
        """
        to get all topologies
        ---
  response_serializer: "TopologyBriefSerializer"

        """
        submit = request.GET.get("submit", "")
        return Response(services.get_all_topologies(submit))

    def post(self, request, format=None):
        """
        to add a topology
        ---
  request_serializer: "TopologyPostSerializer"
  response_serializer: "TopologySerializer"

        """
        return Response(services.add_topology(request.data, self.username))


class TopologyDetailView(BaseView):

    def get(self, request, id, format=None):
        """
        to get a topology by id
        ---
  response_serializer: "TopologySerializer"

        """
        return Response(services.get_topology(int(id)))

    def put(self, request, id, format=None):
        """
        to edit a topology
        ---
  request_serializer: "NameSerializer"

        """
        services.update_topology_name(int(id), request.data, self.username)
        return Response()

    def delete(self, request, id, format=None):
        """
        to delete a topology
        """
        services.delete_topology(int(id))
        return Response()


class TopologySwitchView(BaseView):

    def post(self, request, id, format=None):
        """
        to add a switch
        ---
  request_serializer: "SwitchPostSerializer"
  response_serializer: "TopologySerializer"

        """
        return Response(services.add_topology_switch(int(id), request.data,
                                                     self.username))


class TopologySwitchDetailView(BaseView):

    def put(self, request, tid, sid, format=None):
        """
        to edit a switch in topology
        ---
  request_serializer: "TopologySwitchPutSerializer"
  response_serializer: "TopologySerializer"

        """
        return Response(services.update_topology_switch(int(tid), int(sid),
                                                        request.data,
                                                        self.username))

    def delete(self, request, tid, sid, format=None):
        """
        to delete a switch in topology
        """
        return Response(services.delete_topology_switch(int(tid), int(sid),
                                                        self.username))


class TopologyLinkView(BaseView):

    def post(self, request, id, format=None):
        """
        to add a link for switch in topology
        ---
  request_serializer: "LinkPostSerializer"
  response_serializer: "TopologySerializer"

        """
        return Response(services.add_topology_link(int(id), request.data,
                                                   self.username))


class TopologyLinkDetailView(BaseView):

    def delete(self, request, tid, lid, format=None):
        """
        to delete a link between switch in topology
        ---
  response_serializer: "TopologySerializer"

        """
        return Response(services.delete_topology_link(int(tid), int(lid),
                                                      self.username))


class TopologySubmitView(BaseView):

    def put(self, request, id, format=None):
        """
        to submit the topology
        """
        return Response(services.set_topology_submit(int(id), self.username))


class TopologyClearView(BaseView):

    def put(self, request, id, format=None):
        """
        to clear the topology
        ---
  response_serializer: "TopologySerializer"

        """
        return Response(services.clear_topology(int(id), self.username))


class TopologyDefaultsView(BaseView):

    def put(self, request, id, format=None):
        """
        to edit a topology defaults
        ---
  request_serializer: "TopologyPostDefaultsSerializer"
  response_serializer: "TopologySerializer"

        """
        return Response(services.update_topology_defaults(int(id),
                                                          request.data,
                                                          self.username))


class TopologyCloneView(BaseView):
    def post(self, request, id, format=None):
        """
        To clone a topology
        ---
  request_serializer: "CloneTopoSerializer"
  response_serializer: "TopologySerializer"
        """
        return Response(services.clone_topology(id, request.data,
                                                self.username))


class FabricListView(BaseView):

    def get(self, request, format=None):
        """
        to get all fabrics
        ---
  response_serializer: "FabricBriefSerializer"

        """
        return Response(services.get_all_fabrics())

    def post(self, request, format=None):
        """
        to add a fabric
        ---
  request_serializer: "FabricPostSerializer"
  response_serializer: "FabricSerializer"

        """
        return Response(services.add_fabric(request.data, self.username))


class FabricDetailView(BaseView):

    def get(self, request, id, format=None):
        """
        to get a fabric by id
        ---
  response_serializer: "FabricSerializer"

        """
        return Response(services.get_fabric(int(id)))

    def put(self, request, id, format=None):
        """
        to edit a fabric
        ---
  request_serializer: "NameSerializer"
  response_serializer: "FabricSerializer"

        """
        return Response(services.update_fabric_name(int(id), request.data,
                                                    self.username))

    def delete(self, request, id, format=None):
        """
        to delete a fabric
        """
        services.delete_fabric(int(id))
        return Response()


class FabricSwitchView(BaseView):

    def post(self, request, id, format=None):
        """
        to add a switch in fabric
        ---
  request_serializer: "SwitchPostSerializer"
  response_serializer: "FabricSerializer"

        """
        return Response(services.add_fabric_switch(int(id), request.data,
                                                   self.username))


class FabricSwitchDetailView(BaseView):

    def put(self, request, fid, sid, format=None):
        """
        to edit a switch in fabric
        ---
  request_serializer: "FabricSwitchPutSerializer"
  response_serializer: "FabricSerializer"

        """
        return Response(services.update_fabric_switch(int(fid), int(sid),
                                                      request.data,
                                                      self.username))

    def delete(self, request, fid, sid, format=None):
        """
        to delete a switch in fabric
        ---
  response_serializer: "FabricSerializer"

        """
        return Response(services.delete_fabric_switch(int(fid), int(sid),
                                                      self.username))


class FabricLinkView(BaseView):

    def post(self, request, id, format=None):
        """
        to add a link between switches in fabric
        ---
  request_serializer: "LinkPostSerializer"
  response_serializer: "FabricSerializer"

        """
        return Response(services.add_fabric_link(int(id), request.data,
                                                 self.username))


class FabricLinkDetailView(BaseView):

    def put(self, request, fid, lid, format=None):
        """
        to edit a link in fabric
        ---
  request_serializer: "LinkPutSerializer"
  response_serializer: "FabricSerializer"

        """
        return Response(services.update_fabric_link(int(fid), int(lid),
                                                    request.data,
                                                    self.username))

    def delete(self, request, fid, lid, format=None):
        """
        to delete a link between switch in fabric
        ---
  response_serializer: "FabricSerializer"

        """
        return Response(services.delete_fabric_link(int(fid), int(lid),
                                                    self.username))


class FabricSubmitView(BaseView):

    def put(self, request, id, format=None):
        """
        to submit the fabric
        """
        return Response(services.set_fabric_submit(int(id), self.username))


class FabricDefaultsView(BaseView):

    def put(self, request, id, format=None):
        """
        to edit a fabric defaults
        ---
  request_serializer: "TopologyPostDefaultsSerializer"
  response_serializer: "FabricSerializer"

        """
        return Response(services.update_fabric_defaults(int(id), request.data,
                                                        self.username))


class FabricProfilesView(BaseView):

    def put(self, request, id, format=None):
        """
        to edit a fabric profile
        ---
  request_serializer: "FabricProfilesPutSerializer"
  response_serializer: "FabricSerializer"

        """
        return Response(services.update_fabric_profiles(int(id), request.data,
                                                        self.username))


class FabricBuildView(BaseView):

    def put(self, request, id, format=None):
        """
        to build a config for fabric
        """
        return Response(services.build_fabric_config(int(id)))


class FabricCloneView(BaseView):
    def post(self, request, id, format=None):
        """
        To clone a fabric
        ---
  request_serializer: "CloneFabricSerializer"
  response_serializer: "FabricSerializer"
        """
        return Response(services.clone_fabric(id, request.data, self.username))


class FabricSwtichDecommissionView(BaseView):
    def delete(self, request, fid, sid, format=None):
        """
        To delete a booted swithc in a fabric
        """
        return Response(services.decommission_fabric_switch(int(fid), int(sid),
                                                           self.username))
