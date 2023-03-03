#!/usr/bin/env python
"""
udocker unit tests: CommonLocalFileApi
"""
import pytest
from udocker.commonlocalfile import CommonLocalFileApi


@pytest.fixture
def lrepo(mocker):
    mock_lrepo = mocker.patch('udocker.container.localrepo.LocalRepository')
    return mock_lrepo


@pytest.fixture
def clfapi(mocker, lrepo):
    return CommonLocalFileApi(lrepo)


def test_02__move_layer_to_v1repo(mocker, clfapi):
    """Test02 CommonLocalFileApi()._move_layer_to_v1repo(). filepath and layerid empty"""
    layer_id = ""
    filepath = ""
    mock_layersdir = mocker.patch('udocker.container.localrepo.LocalRepository.layersdir')
    status = clfapi._move_layer_to_v1repo(filepath, layer_id)
    assert not status
    mock_layersdir.assert_not_called()


data_in = (("/home/.udocker/12345.json", "12345"),
                ("/home/.udocker/12345.layer.tar", "12345"),
                ("/home/.udocker/12345", "some:12345"))

@pytest.mark.parametrize("fpath,lid", data_in)
def test_03__move_layer_to_v1repo(mocker, clfapi, lrepo, fpath, lid):
    """Test03 CommonLocalFileApi()._move_layer_to_v1repo(). filepath not empty"""
    layer_id = lid
    filepath = fpath
    mock_rename = mocker.patch('os.rename')
    mock_copy = mocker.patch('udocker.commonlocalfile.FileUtil.copyto')
    lrepo.return_value.layersdir = "/home/.udocker"
    lrepo.return_value.add_image_layer.return_value = True

    status = clfapi._move_layer_to_v1repo(filepath, layer_id)
    assert status
    mock_rename.assert_called()
    lrepo.add_image_layer.assert_called()
    mock_copy.assert_not_called()


def test_04__move_layer_to_v1repo(mocker, clfapi, lrepo):
    """Test04 CommonLocalFileApi()._move_layer_to_v1repo(). raises OSError"""
    layer_id = "12345"
    filepath = "/home/.udocker/12345.layer.tar"
    mock_rename = mocker.patch('os.rename', side_effect=OSError("fail"))
    mock_copy = mocker.patch('udocker.commonlocalfile.FileUtil.copyto', return_value=False)
    lrepo.return_value.layersdir = "/home/.udocker"
    lrepo.return_value.add_image_layer.return_value = True

    status = clfapi._move_layer_to_v1repo(filepath, layer_id)
    assert not status
    mock_rename.assert_called()
    lrepo.add_image_layer.assert_not_called()
    mock_copy.assert_called()


def test_05__load_image(clfapi, lrepo):
    """Test05 CommonLocalFileApi()._load_image().cd_imagerepo True"""
    structure = "12345"
    imagerepo = "/home/.udocker/images"
    tag = "v1"
    lrepo.cd_imagerepo.return_value = True

    status = clfapi._load_image(structure, imagerepo, tag)
    assert status == []
    lrepo.cd_imagerepo.assert_called()
    lrepo.setup_imagerepo.assert_not_called()


def test_06__load_image(clfapi, lrepo):
    """Test06 CommonLocalFileApi()._load_image().cd_imagerepo False"""
    structure = "12345"
    imagerepo = "/home/.udocker/images"
    tag = "v1"
    lrepo.cd_imagerepo.return_value = False
    lrepo.setup_imagerepo.return_value = True
    lrepo.setup_tag.return_value = False

    status = clfapi._load_image(structure, imagerepo, tag)
    assert status == []
    lrepo.cd_imagerepo.assert_called()
    lrepo.setup_imagerepo.assert_called()
    lrepo.setup_tag.assert_called()
    lrepo.set_version.assert_not_called()


def test_07__load_image(clfapi, lrepo):
    """Test07 CommonLocalFileApi()._set version False"""
    structure = "12345"
    imagerepo = "/home/.udocker/images"
    tag = "v1"
    lrepo.cd_imagerepo.return_value = False
    lrepo.setup_imagerepo.return_value = True
    lrepo.setup_tag.return_value = True
    lrepo.set_version.return_value = False

    status = clfapi._load_image(structure, imagerepo, tag)
    assert status == []
    lrepo.cd_imagerepo.assert_called()
    lrepo.setup_imagerepo.assert_called()
    lrepo.setup_tag.assert_called()
    lrepo.set_version.assert_called()


def test_08__load_image(mocker, clfapi, lrepo):
    """Test08 CommonLocalFileApi()._set version True"""
    structure = "12345"
    imagerepo = "/home/.udocker/images"
    tag = "v1"
    lrepo.cd_imagerepo.return_value = False
    lrepo.setup_imagerepo.return_value = True
    lrepo.setup_tag.return_value = True
    lrepo.set_version.return_value = True
    mock_imgstep2 = mocker.patch.object(CommonLocalFileApi, '_load_image_step2', return_value=True)

    status = clfapi._load_image(structure, imagerepo, tag)
    assert status
    lrepo.cd_imagerepo.assert_called()
    lrepo.setup_imagerepo.assert_called()
    lrepo.setup_tag.assert_called()
    lrepo.set_version.assert_called()
    mock_imgstep2.assert_called()


def test_09__untar_saved_container(mocker, clfapi):
    """Test09 CommonLocalFileApi()._untar_saved_container()."""
    tarfile = "file.tar"
    destdir = "/home/.udocker/images"
    mock_ucall = mocker.patch('udocker.commonlocalfile.Uprocess.call', return_value=True)

    status = clfapi._untar_saved_container(tarfile, destdir)
    assert not status
    mock_ucall.assert_called()


def test_10_create_container_meta(mocker, clfapi):
    """Test10 CommonLocalFileApi().create_container_meta()."""
    layer_id = "12345"
    comment = "created by my udocker"
    mock_arch = mocker.patch('udocker.commonlocalfile.HostInfo.arch', return_value="x86_64")
    mock_version = mocker.patch('udocker.commonlocalfile.HostInfo.osversion', return_value="8")
    mock_size = mocker.patch('udocker.commonlocalfile.FileUtil.size', return_value=-1)

    status = clfapi.create_container_meta(layer_id, comment)
    assert status["id"] == layer_id
    assert status["comment"] == comment
    assert status["size"] == 0
    mock_arch.assert_called()
    mock_version.assert_called()
    mock_size.assert_called()


def test_11_import_toimage(mocker, clfapi, lrepo):
    """Test11 CommonLocalFileApi().import_toimage(). path exists False"""
    mock_exists = mocker.patch('os.path.exists', return_value=False)
    mock_logerr = mocker.patch('udocker.LOG.error')
    lrepo.setup_imagerepo.return_value = True

    status = clfapi.import_toimage("img.tar", "/images", "v1")
    assert not status
    mock_exists.assert_called()
    mock_logerr.assert_called()
    lrepo.setup_imagerepo.assert_not_called()


def test_12_import_toimage(mocker, clfapi, lrepo):
    """Test12 CommonLocalFileApi().import_toimage(). path exists True"""
    mock_exists = mocker.patch('os.path.exists', return_value=True)
    mock_logerr = mocker.patch('udocker.LOG.error')
    mock_loginf = mocker.patch('udocker.LOG.info')
    lrepo.setup_imagerepo.return_value = True
    lrepo.cd_imagerepo.return_value = '/tag'
    lrepo.setup_tag.return_value = ''

    status = clfapi.import_toimage("img.tar", "/images", "v1")
    assert not status
    mock_exists.assert_called()
    mock_logerr.assert_not_called()
    lrepo.setup_imagerepo.assert_called()
    lrepo.cd_imagerepo.assert_called()
    mock_loginf.assert_called()
    lrepo.setup_tag.assert_not_called()


def test_13_import_toimage(mocker, clfapi, lrepo):
    """Test13 CommonLocalFileApi().import_toimage(). path exists True tag not exist"""
    mock_exists = mocker.patch('os.path.exists', return_value=True)
    mock_logerr = mocker.patch('udocker.LOG.error')
    mock_loginf = mocker.patch('udocker.LOG.info')
    lrepo.setup_imagerepo.return_value = True
    lrepo.cd_imagerepo.return_value = ''
    lrepo.setup_tag.return_value = ''
    lrepo.set_version.return_value = False

    status = clfapi.import_toimage("img.tar", "/images", "v1")
    assert not status
    mock_exists.assert_called()
    mock_logerr.assert_called()
    lrepo.setup_imagerepo.assert_called()
    lrepo.cd_imagerepo.assert_called()
    mock_loginf.assert_not_called()
    lrepo.setup_tag.assert_called()
    lrepo.set_version.assert_not_called()


def test_14_import_toimage(mocker, clfapi, lrepo):
    """Test14 CommonLocalFileApi().import_toimage(). tag exist set version False"""
    mock_exists = mocker.patch('os.path.exists', return_value=True)
    mock_logerr = mocker.patch('udocker.LOG.error')
    mock_loginf = mocker.patch('udocker.LOG.info')
    mock_layerv1 = mocker.patch('udocker.commonlocalfile.Unique.layer_v1')
    lrepo.setup_imagerepo.return_value = True
    lrepo.cd_imagerepo.return_value = ''
    lrepo.setup_tag.return_value = 'tag'
    lrepo.set_version.return_value = False

    status = clfapi.import_toimage("img.tar", "/images", "v1")
    assert not status
    mock_exists.assert_called()
    mock_logerr.assert_called()
    lrepo.setup_imagerepo.assert_called()
    lrepo.cd_imagerepo.assert_called()
    mock_loginf.assert_not_called()
    lrepo.setup_tag.assert_called()
    lrepo.set_version.assert_called()
    mock_layerv1.assert_not_called()


def test_15_import_toimage(mocker, clfapi, lrepo):
    """Test15 CommonLocalFileApi().import_toimage(). set version True copyto False"""
    mock_exists = mocker.patch('os.path.exists', side_effect=[True, False])
    mock_logerr = mocker.patch('udocker.LOG.error')
    mock_loginf = mocker.patch('udocker.LOG.info')
    mock_layerv1 = mocker.patch('udocker.commonlocalfile.Unique.layer_v1', return_value='123')
    mock_rename = mocker.patch('os.rename', return_value=True)
    mock_copy = mocker.patch('udocker.commonlocalfile.FileUtil.copyto', return_value=False)
    lrepo.setup_imagerepo.return_value = True
    lrepo.cd_imagerepo.return_value = ''
    lrepo.setup_tag.return_value = 'tag'
    lrepo.set_version.return_value = True
    lrepo.layersdir.return_value = '/layers'

    status = clfapi.import_toimage("img.tar", "/images", "v1")
    assert not status
    assert mock_exists.call_count == 2
    mock_logerr.assert_called()
    lrepo.setup_imagerepo.assert_called()
    lrepo.cd_imagerepo.assert_called()
    mock_loginf.assert_not_called()
    lrepo.setup_tag.assert_called()
    lrepo.set_version.assert_called()
    mock_layerv1.assert_called()
    mock_rename.assert_called()
    mock_copy.assert_called()


def test_16_import_toimage(mocker, clfapi, lrepo):
    """Test16 CommonLocalFileApi().import_toimage(). return layerid"""
    mock_exists = mocker.patch('os.path.exists', side_effect=[True, True])
    mock_logerr = mocker.patch('udocker.LOG.error')
    mock_loginf = mocker.patch('udocker.LOG.info')
    mock_layerv1 = mocker.patch('udocker.commonlocalfile.Unique.layer_v1', return_value='123')
    mock_rename = mocker.patch('os.rename', return_value=True)
    mock_copy = mocker.patch('udocker.commonlocalfile.FileUtil.copyto', return_value=False)
    mock_contmeta = mocker.patch.object(CommonLocalFileApi, 'create_container_meta')
    lrepo.setup_imagerepo.return_value = True
    lrepo.cd_imagerepo.return_value = ''
    lrepo.setup_tag.return_value = 'tag'
    lrepo.set_version.return_value = True
    lrepo.layersdir.return_value = '/layers'
    lrepo.add_image_layer.side_effect = [True, True]
    lrepo.save_json.side_effect = [True, True]

    status = clfapi.import_toimage("img.tar", "/images", "v1")
    assert status == '123'
    assert mock_exists.call_count == 2
    assert lrepo.add_image_layer.call_count == 2
    assert lrepo.save_json.call_count == 2
    mock_logerr.assert_not_called()
    lrepo.setup_imagerepo.assert_called()
    lrepo.cd_imagerepo.assert_called()
    mock_loginf.assert_called()
    lrepo.setup_tag.assert_called()
    lrepo.set_version.assert_called()
    mock_layerv1.assert_called()
    mock_rename.assert_called()
    mock_copy.assert_not_called()
    mock_contmeta.assert_called()


# @patch('udocker.commonlocalfile.ContainerStructure.create_fromlayer')
# @patch('udocker.commonlocalfile.Unique.layer_v1')
# @patch('udocker.commonlocalfile.os.path.exists')
# def test_08_import_tocontainer(self, mock_exists, mock_layerv1, mock_create):
#     """Test08 CommonLocalFileApi().import_tocontainer()."""
#     tarfile = ""
#     imagerepo = ""
#     tag = ""
#     container_name = ""
#     mock_exists.return_value = False
#     clfapi = CommonLocalFileApi(self.local)
#     status = clfapi.import_tocontainer(tarfile, imagerepo, tag, container_name)
#     self.assertFalse(status)

#     tarfile = "img.tar"
#     imagerepo = "/home/.udocker/images"
#     tag = "v1"
#     container_name = "mycont"
#     self.local.get_container_id.return_value = True
#     mock_exists.return_value = True
#     clfapi = CommonLocalFileApi(self.local)
#     status = clfapi.import_tocontainer(tarfile, imagerepo, tag, container_name)
#     self.assertTrue(self.local.get_container_id.called)
#     self.assertTrue(mock_exists.called)
#     self.assertFalse(status)

#     tarfile = "img.tar"
#     imagerepo = "/home/.udocker/images"
#     tag = "v1"
#     container_name = "mycont"
#     self.local.get_container_id.return_value = False
#     self.local.set_container_name.return_value = True
#     mock_exists.return_value = True
#     mock_layerv1.return_value = "12345"
#     mock_create.return_value = "345"
#     clfapi = CommonLocalFileApi(self.local)
#     status = clfapi.import_tocontainer(tarfile, imagerepo, tag, container_name)
#     self.assertTrue(self.local.get_container_id.called)
#     self.assertTrue(mock_exists.called)
#     self.assertTrue(mock_layerv1.called)
#     self.assertTrue(mock_create.called)
#     self.assertEqual(status, "345")

# @patch('udocker.commonlocalfile.ContainerStructure.clone_fromfile')
# @patch('udocker.commonlocalfile.os.path.exists')
# def test_09_import_clone(self, mock_exists, mock_clone):
#     """Test09 CommonLocalFileApi().import_clone()."""
#     tarfile = ""
#     container_name = ""
#     mock_exists.return_value = False
#     clfapi = CommonLocalFileApi(self.local)
#     status = clfapi.import_clone(tarfile, container_name)
#     self.assertFalse(status)

#     tarfile = "img.tar"
#     container_name = "mycont"
#     self.local.get_container_id.return_value = True
#     mock_exists.return_value = True
#     clfapi = CommonLocalFileApi(self.local)
#     status = clfapi.import_clone(tarfile, container_name)
#     self.assertTrue(self.local.get_container_id.called)
#     self.assertTrue(mock_exists.called)
#     self.assertFalse(status)

#     tarfile = "img.tar"
#     container_name = "mycont"
#     self.local.get_container_id.return_value = False
#     self.local.set_container_name.return_value = True
#     mock_exists.return_value = True
#     mock_clone.return_value = "345"
#     clfapi = CommonLocalFileApi(self.local)
#     status = clfapi.import_clone(tarfile, container_name)
#     self.assertTrue(self.local.get_container_id.called)
#     self.assertTrue(mock_exists.called)
#     self.assertTrue(mock_clone.called)
#     self.assertEqual(status, "345")

# @patch('udocker.commonlocalfile.ExecutionMode.set_mode')
# @patch('udocker.commonlocalfile.ExecutionMode.get_mode')
# @patch('udocker.commonlocalfile.ContainerStructure.clone')
# def test_10_clone_container(self, mock_clone, mock_exget, mock_exset):
#     """Test10 CommonLocalFileApi().clone_container()."""
#     container_name = "mycont"
#     container_id = ""
#     self.local.get_container_id.return_value = True
#     clfapi = CommonLocalFileApi(self.local)
#     status = clfapi.clone_container(container_id, container_name)
#     self.assertFalse(status)

#     container_name = "mycont"
#     container_id = ""
#     self.local.get_container_id.return_value = False
#     self.local.set_container_name.return_value = True
#     mock_clone.return_value = "345"
#     mock_exget.return_value = "P1"
#     mock_exset.return_value = True
#     clfapi = CommonLocalFileApi(self.local)
#     status = clfapi.clone_container(container_id, container_name)
#     self.assertTrue(self.local.get_container_id.called)
#     self.assertTrue(self.local.set_container_name.called)
#     self.assertTrue(mock_exget.called)
#     self.assertFalse(mock_exset.called)
#     self.assertTrue(mock_clone.called)
#     self.assertEqual(status, "345")

#     container_name = "mycont"
#     container_id = ""
#     self.local.get_container_id.return_value = False
#     self.local.set_container_name.return_value = True
#     mock_clone.return_value = "345"
#     mock_exget.return_value = "F1"
#     mock_exset.return_value = True
#     clfapi = CommonLocalFileApi(self.local)
#     status = clfapi.clone_container(container_id, container_name)
#     self.assertTrue(self.local.get_container_id.called)
#     self.assertTrue(self.local.set_container_name.called)
#     self.assertTrue(mock_exget.called)
#     self.assertTrue(mock_exset.called)
#     self.assertTrue(mock_clone.called)
#     self.assertEqual(status, "345")

# @patch('udocker.commonlocalfile.os.path.exists')
# def test_11__get_imagedir_type(self, mock_exists):
#     """Test11 CommonLocalFileApi()._get_imagedir_type()."""
#     tmp_imagedir = "/home/.udocker/images/myimg"
#     mock_exists.side_effect = [False, False]
#     clfapi = CommonLocalFileApi(self.local)
#     status = clfapi._get_imagedir_type(tmp_imagedir)
#     self.assertEqual(status, "")

#     mock_exists.side_effect = [True, False]
#     clfapi = CommonLocalFileApi(self.local)
#     status = clfapi._get_imagedir_type(tmp_imagedir)
#     self.assertEqual(status, "OCI")

#     mock_exists.side_effect = [False, True]
#     clfapi = CommonLocalFileApi(self.local)
#     status = clfapi._get_imagedir_type(tmp_imagedir)
#     self.assertEqual(status, "Docker")
